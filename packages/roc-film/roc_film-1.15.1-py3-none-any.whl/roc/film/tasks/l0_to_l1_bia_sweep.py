#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains task to create the RPW L1 Bias sweep CDF files."""

import os
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from sqlalchemy import and_
import numpy as np

from poppy.core.logger import logger
from poppy.core.task import Task
from poppy.core.target import FileTarget
from poppy.core.db.connector import Connector
from roc.rap.tasks.bia.current import raw_to_na

from roc.rpl.time import Time

from roc.dingo.models.data import EventLog
from roc.dingo.tools import query_db, get_columns

from roc.film.tasks.db_to_anc_bia_sweep_table import DbToAncBiaSweepTable
from roc.film.constants import (
    ANT_1_FLAG,
    ANT_2_FLAG,
    ANT_3_FLAG,
    PIPELINE_DATABASE,
    TRYOUTS,
    SQL_LIMIT,
    TIME_WAIT_SEC,
    BIA_SWEEP_TABLE_PACKETS,
)
from roc.film.tools.l0 import L0
from roc.film.tools.file_helpers import (
    l0_to_trange_cdf,
    get_l0_trange,
    get_l0_files,
    get_output_dir,
    is_output_dir,
)

__all__ = ["L0ToL1BiaSweep"]


class L0ToL1BiaSweep(Task):
    plugin_name = "roc.film"
    name = "l0_to_l1_bia_sweep"

    def add_targets(self):
        self.add_input(
            target_class=FileTarget,
            identifier="l0_file",
            filepath=get_l0_files,
            many=True,
        )

        self.add_output(target_class=FileTarget, identifier="l1_bia_sweep")

    def setup_inputs(self):
        """Initialize inputs for the task"""

        # get a database session, table model and table columns (except primary key)
        self.session = Connector.manager[PIPELINE_DATABASE].session
        self.model = EventLog
        self.columns = get_columns(self.model, remove=["id"])

        # Get tryouts from pipeline properties
        self.tryouts = self.pipeline.get("tryouts", default=[TRYOUTS], create=True)[0]

        # Get wait from pipeline properties
        self.wait = self.pipeline.get("wait", default=[TIME_WAIT_SEC], create=True)[0]

        # Retrieve --limit keyword value
        self.limit = self.pipeline.get(
            "limit",
            default=[SQL_LIMIT],
        )[0]

        # Get products directory (folder where final output files will be
        # moved)
        self.products_dir = self.pipeline.get(
            "products_dir", default=[None], args=True
        )[0]

        # Get output dir
        self.output_dir = get_output_dir(self.pipeline)
        if not is_output_dir(self.output_dir, products_dir=self.products_dir):
            logger.info(f"Making {self.output_dir}")
            os.makedirs(self.output_dir)
        else:
            logger.debug(f"Output files will be saved into folder {self.output_dir}")

        # Get (optional) arguments for SPICE
        predictive = self.pipeline.get("predictive", default=False, args=True)
        kernel_date = self.pipeline.get("kernel_date", default=None, args=True)
        no_spice = self.pipeline.get("no_spice", default=False, args=True)

        # Get/create Time singleton
        self.time = Time(
            predictive=predictive, kernel_date=kernel_date, no_spice=no_spice
        )

        # Get list of input l0 file(s)
        self.l0_file_list = self.inputs["l0_file"].filepath
        self.l0_file_num = len(self.l0_file_list)

        # Get L0 files time_min/time_max
        l0_time_min, l0_time_max = get_l0_trange(self.l0_file_list)

        # Define output file start time
        self.start_time = self.pipeline.get("start_time", default=[None])[0]
        if not self.start_time:
            self.start_time = min(l0_time_min)
        logger.debug(f"start_time value is {self.start_time}")

        # Define output file end time
        self.end_time = self.pipeline.get("end_time", default=[None])[0]
        if not self.end_time:
            self.end_time = max(l0_time_max)
        logger.debug(f"end_time value is {self.end_time}")

        # Get or create failed_files list from pipeline properties
        self.failed_files = self.pipeline.get("failed_files", default=[], create=True)

        # Get or create processed_files list from pipeline properties
        self.processed_files = self.pipeline.get(
            "processed_files", default=[], create=True
        )

        # Get force optional keyword
        self.force = self.pipeline.get("force", default=False, args=True)

        # Get overwrite argument
        self.overwrite = self.pipeline.get("overwrite", default=False, args=True)

        # Get cdag keyword
        self.is_cdag = self.pipeline.get("cdag", default=False, args=True)

        return True

    def run(self):
        # Import external classes, methods
        from spacepy.pycdf import CDF

        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.info(f"Task {self.job_id} is starting")
        try:
            self.setup_inputs()
        except Exception as e:
            logger.exception(f"Initializing inputs has failed for {self.job_id}:\n{e}")
            try:
                os.makedirs(os.path.join(self.output_dir, "failed"))
            except Exception as e:
                logger.error(f"output_dir argument is not defined:\n{e}")
            self.pipeline.exit()
            return

        # return list of sweep tables from pipeline.event_log table
        # (as a pandas.DataFrame object)
        self.sweep_table_list = self.load_sweep_tables()
        if self.sweep_table_list.shape[0] == 0:
            return

        # Get start times/end times of the Bias sweeps
        logger.info(
            f"building sweep info list from {self.l0_file_num} input L0 files..."
        )
        bia_sweep_list = self.build_sweep_info_list(
            self.l0_file_list, self.sweep_table_list
        )
        bia_sweep_num = len(bia_sweep_list)
        if bia_sweep_num == 0:
            logger.info("No Bias sweep found")
            return
        else:
            logger.info(f"{bia_sweep_num} Bias sweeps to process")

        # Loop over each Bias sweep
        for i, current_sweep in enumerate(bia_sweep_list):
            # Get start_time/end_time of current sweep
            bia_sweep_start_time = current_sweep["start_time"]
            bia_sweep_end_time = current_sweep["end_time"]
            logger.info(
                f"Processing Bias sweep between {current_sweep['start_time']} and "
                f"{current_sweep['end_time']}... ({bia_sweep_num - i} sweeps remaining)"
            )

            # Generate output L1 CDF with LFR CWF F3 data, but not Bias sweep
            # current values.
            l1_cdf_path = None
            try:
                l1_cdf_path = l0_to_trange_cdf(
                    self,
                    "l0_to_l1_bia_sweep",
                    self.l0_file_list,
                    self.output_dir,
                    time_instance=self.time,
                    start_time=bia_sweep_start_time,
                    end_time=bia_sweep_end_time,
                    overwrite=self.overwrite,
                    is_cdag=self.is_cdag,
                )
            except Exception:
                if l1_cdf_path and l1_cdf_path[0] not in self.failed_files:
                    self.failed_files.append(l1_cdf_path[0])
                else:
                    # TODO - Improve this part:
                    #  What to do if the process has failed
                    #  before output file has been generated
                    self.failed_files.append(
                        (
                            Path(self.output_dir) / Path("l0_to_l1_bia_sweep.failed")
                        ).touch()
                    )

                logger.exception(
                    "Filling L1 Bias sweep CDF with TM BIAS CALIB data has failed!"
                )

            # If output L1 CDF has been correctly generated, then insert Bias
            # sweep current values
            if l1_cdf_path and os.path.isfile(l1_cdf_path[0]):
                # Open CDF and loop over each Epoch time
                logger.info(
                    f"Filling {l1_cdf_path[0]} file with Bias current values..."
                )
                try:
                    with CDF(l1_cdf_path[0]) as cdf:
                        cdf.readonly(False)
                        epoch_values = cdf["Epoch"][:]

                        for i, current_epoch in enumerate(epoch_values):
                            # For each epoch time get values of bias intensity on
                            # each antenna
                            current_sweep_idx = self._get_sweep_step_idx(
                                current_epoch, current_sweep
                            )

                            if current_sweep_idx is None:
                                logger.debug(
                                    f"No sweep value found for {current_epoch} "
                                    f"(start_time={current_sweep['start_time']} and"
                                    f" end_time={current_sweep['end_time']})"
                                )
                            else:
                                cdf["BIAS_SWEEP_CURRENT"][i, 0] = current_sweep[
                                    "step_ibias"
                                ][current_sweep_idx][0]
                                cdf["BIAS_SWEEP_CURRENT"][i, 1] = current_sweep[
                                    "step_ibias"
                                ][current_sweep_idx][1]
                                cdf["BIAS_SWEEP_CURRENT"][i, 2] = current_sweep[
                                    "step_ibias"
                                ][current_sweep_idx][2]

                                # Fill ant flag
                                cdf["ANT_FLAG"][i] = current_sweep["ant_flag"][
                                    current_sweep_idx
                                ]

                                # Fill bypass
                                cdf["BIAS_MODE_BYPASS_PROBE1"][i] = current_sweep[
                                    "bypass"
                                ][current_sweep_idx][0]
                                cdf["BIAS_MODE_BYPASS_PROBE2"][i] = current_sweep[
                                    "bypass"
                                ][current_sweep_idx][1]
                                cdf["BIAS_MODE_BYPASS_PROBE3"][i] = current_sweep[
                                    "bypass"
                                ][current_sweep_idx][2]

                except Exception:
                    logger.exception(
                        "Filling L1 Bias sweep CDF with Bias sweep intensity data has failed!"
                    )
                    if l1_cdf_path[0] not in self.failed_files:
                        self.failed_files.append(l1_cdf_path[0])
                else:
                    logger.info(f"{l1_cdf_path[0]} filled with Bias sweep intensities")
                    if l1_cdf_path[0] not in self.processed_files:
                        self.processed_files.append(l1_cdf_path[0])

    def _get_sweep_step_idx(self, current_time, current_sweep):
        """
        Get the index of the sweep for the current time

        :param current_time: time for which sweep index must be returned
        :param current_sweep: List of sweeps
        :return: index of sweep for the input time
        """

        i = np.where(
            np.array(current_sweep["step_time"], dtype=datetime) <= current_time
        )
        try:
            return i[0][-1]
        except Exception:
            return None

    def build_sweep_info_list(self, l0_file_list, sweep_table_list):
        """
        Build list of Bias sweep data from info in l0 files

        :param l0_file_list: List of input L0 files
        :param sweep_table_list: List of bias sweep tables
        :return: list of bias sweep info (time + parameters)
        """

        # Initialize output list
        sweep_info_list = []

        # List of Bias sweep packet to retrieve from l0
        bias_sweep_expected_packet_list = [
            "TM_DPU_EVENT_PR_BIA_SWEEP",
            "TC_DPU_START_BIAS_SWEEP",
            "TM_DPU_BIA_HK",
        ]

        # Extract wanted packets and re-order by increasing time
        bia_sweep_packet_list = L0.l0_to_packet_list(
            l0_file_list,
            include=bias_sweep_expected_packet_list,
            start_time=self.start_time,
            end_time=self.end_time,
            ascending=True,
        )

        bia_sweep_packet_num = len(bia_sweep_packet_list)
        if bia_sweep_packet_num == 0:
            logger.info(
                f"No {','.join(bias_sweep_expected_packet_list)} found in the "
                f"input l0 file list"
            )
            return sweep_info_list

        # Initialize loop variables
        # Flag to indicate that a sweep is running at current time
        is_running = False
        # List of progress code values for the current sweep
        current_sweep_pr_code_list = []

        # Loop over each packet time in the sweep info list
        for packet_idx, current_packet in enumerate(bia_sweep_packet_list):
            current_time = current_packet["utc_time"]
            current_name = current_packet["palisade_id"]
            current_idb_source = current_packet["idb_source"]
            current_idb_version = current_packet["idb_version"]

            # if current packet is a bias sweep start event
            if current_name == "TM_DPU_EVENT_PR_BIA_SWEEP":
                # Get Bias sweep progress code
                sweep_pr_code = int(current_packet["PA_DPU_BIA_SWEEP_PR_CODE"])

                # Update current time to use PA_DPU_BIA_SWEEP_TIME (UTC) instead of
                # packet creation on-board time
                current_time = Time().obt_to_utc(
                    np.array(
                        current_packet["PA_DPU_BIA_SWEEP_TIME"][:2], dtype=int
                    ).reshape([1, 2]),
                    to_datetime=True,
                )[0]

                logger.debug(
                    f"{packet_idx}: TM_DPU_EVENT_PR_BIA_SWEEP at {current_time} "
                    f"with sweep_pr_code {sweep_pr_code} "
                    f"(running status is {is_running})"
                )

                # If event indicates a sweep start on ANT1 (START_ANT1 == 1)
                # ...
                if sweep_pr_code == 1:
                    # Set current ant flag
                    current_ant_flag = ANT_1_FLAG

                    # Set current sweep start time (for current antenna)
                    current_sweep_start = current_time

                    # Initialize sweep setting dict for current sweep
                    current_sweep_setting = {}  # Store current sweep setting

                    # Go backward in the list to find the
                    # latest passed TC_DPU_START_BIAS_SWEEP used
                    # to set sweep parameters as well as
                    # latest HK_BIA_MODE_BYPASS_PROBE1/2/3 parameters
                    # in TM_DPU_BIA_HK
                    # And put them into the setting
                    prev_packet_idx = packet_idx
                    has_full_setting = [False, False]
                    while prev_packet_idx >= 0:
                        prev_packet = bia_sweep_packet_list[prev_packet_idx]
                        if (
                            prev_packet["palisade_id"] == "TC_DPU_START_BIAS_SWEEP"
                            and prev_packet["tc_exe_state"] == "PASSED"
                        ):
                            # bias sweep step duration in sec
                            current_sweep_setting["step_sec"] = prev_packet[
                                "CP_DPU_BIA_SWEEP_DURATION"
                            ]

                            current_sweep_setting["ibias_1_def"] = raw_to_na(
                                prev_packet["CP_DPU_BIA_SWEEP_ANT_1_CUR"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float)
                            current_sweep_setting["ibias_2_def"] = raw_to_na(
                                prev_packet["CP_DPU_BIA_SWEEP_ANT_2_CUR"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float)
                            current_sweep_setting["ibias_3_def"] = raw_to_na(
                                prev_packet["CP_DPU_BIA_SWEEP_ANT_3_CUR"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float)
                            has_full_setting[0] = True
                        elif prev_packet["palisade_id"] == "TM_DPU_BIA_HK":
                            current_sweep_setting["bypass_1"] = prev_packet[
                                "HK_BIA_MODE_BYPASS_PROBE1"
                            ]
                            current_sweep_setting["bypass_2"] = prev_packet[
                                "HK_BIA_MODE_BYPASS_PROBE2"
                            ]
                            current_sweep_setting["bypass_3"] = prev_packet[
                                "HK_BIA_MODE_BYPASS_PROBE3"
                            ]
                            has_full_setting[1] = True

                        if all(has_full_setting):
                            break

                        prev_packet_idx -= 1

                    # if no TC_DPU_START_BIAS_SWEEP found
                    if prev_packet_idx < 0 and not all(has_full_setting):
                        logger.warning(
                            "No TC_DPU_START_BIAS_SWEEP and/or TM_DPU_BIA_HK data found "
                            "in input L0 files for current sweep, skipping"
                        )
                        is_running = False
                        continue

                    # Initialize info dict for current sweep info
                    current_sweep_info = {
                        "sweep_pr_code": [],
                        "step_time": [],
                        "step_ibias": [],
                        "ant_flag": [],
                        "bypass": [],
                    }

                    # Set sweep start time
                    current_sweep_info["start_time"] = current_time

                    # Set is_running flag to True
                    is_running = True

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep step on ANT1 (STEP_ANT1 == 7) ...
                elif sweep_pr_code == 7 and is_running:
                    # Set current sweep dictionary with actual values
                    current_sweep_info["step_time"].append(current_time)
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)
                    current_sweep_info["step_ibias"].append(
                        [
                            raw_to_na(
                                current_packet["PA_DPU_BIA_SWEEP_VALUE"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float),
                            current_sweep_setting["ibias_2_def"],
                            current_sweep_setting["ibias_3_def"],
                        ]
                    )

                    # Save progress code
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                    # Save antenna flag
                    current_sweep_info["ant_flag"].append(current_ant_flag)

                    # Save bypass values
                    current_sweep_info["bypass"].append(
                        [
                            current_sweep_setting["bypass_1"],
                            current_sweep_setting["bypass_2"],
                            current_sweep_setting["bypass_3"],
                        ]
                    )

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep end on ANT1 (END_ANT1 == 2)
                # ...
                elif sweep_pr_code == 2 and is_running:
                    # If it is not a step-by-step sweep, then compute sweep times and intensities in nA
                    # from the latest sweep table values
                    if current_sweep_pr_code_list[-1] == 1:
                        # Get latest sweep table status
                        current_sweep_table = (
                            DbToAncBiaSweepTable.get_latest_sweep_table(
                                current_time, sweep_table_list
                            )
                        )
                        if current_sweep_table.shape[0] == 0:
                            logger.info(
                                f"No valid bias sweep table found for {str(current_time)}"
                            )
                            is_running = False
                            continue

                        if current_sweep_table["TC_NAME"] == "TC_DPU_CLEAR_BIAS_SWEEP":
                            logger.warning(
                                "On-board sweep table seems to be empty "
                                f"(TC_DPU_CLEAR_BIAS_SWEEP executed on {current_sweep_table['TC_EXE_UTC_TIME']})"
                            )
                            is_running = False
                            continue

                        # Build array of intensity current values versus time for
                        # current sweep

                        current_table_data = current_sweep_table["BIA_SWEEP_TABLE_CUR"]
                        current_table_size = len(current_table_data)
                        for j in range(current_table_size):
                            # If no valid value in the table, skip current step
                            if not current_table_data[j]:
                                continue

                            # Save absolute time of current sweep step
                            current_sweep_info["step_time"].append(
                                current_sweep_start
                                + timedelta(
                                    seconds=int(j * current_sweep_setting["step_sec"])
                                )
                            )

                            # Save Bias intensity values on the three antennas
                            current_sweep_info["step_ibias"].append(
                                [
                                    current_table_data[j],
                                    current_sweep_setting["ibias_2_def"],
                                    current_sweep_setting["ibias_3_def"],
                                ]
                            )

                            # Save progress code
                            current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                            # Save antenna flag
                            current_sweep_info["ant_flag"].append(current_ant_flag)

                            # Save bypass values
                            current_sweep_info["bypass"].append(
                                [
                                    current_sweep_setting["bypass_1"],
                                    current_sweep_setting["bypass_2"],
                                    current_sweep_setting["bypass_3"],
                                ]
                            )

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep start on ANT2 (START_ANT2 == 3)
                # ...
                elif sweep_pr_code == 3 and is_running:
                    # Set current ant flag
                    current_ant_flag = ANT_2_FLAG

                    # Set current sweep start time (for current antenna)
                    current_sweep_start = current_time

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep step on ANT2 (STEP_ANT2 == 8) ...
                elif sweep_pr_code == 8 and is_running:
                    # Set current sweep dictionary with actual values
                    current_sweep_info["step_time"].append(current_time)
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)
                    current_sweep_info["step_ibias"].append(
                        [
                            current_sweep_setting["ibias_1_def"],
                            raw_to_na(
                                current_packet["PA_DPU_BIA_SWEEP_VALUE"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float),
                            current_sweep_setting["ibias_3_def"],
                        ]
                    )

                    # Save progress code
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                    # Save antenna flag
                    current_sweep_info["ant_flag"].append(current_ant_flag)

                    # Save bypass values
                    current_sweep_info["bypass"].append(
                        [
                            current_sweep_setting["bypass_1"],
                            current_sweep_setting["bypass_2"],
                            current_sweep_setting["bypass_3"],
                        ]
                    )

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep end on ANT2 (END_ANT2 == 4) ...
                elif sweep_pr_code == 4 and is_running:
                    # If it is not a step-by-step sweep, then compute sweep times and intensities in nA
                    # from the latest sweep table values
                    if current_sweep_pr_code_list[-1] == 3:
                        for j in range(current_table_size):
                            # If no valid value in the table, skip current step
                            if not current_table_data[j]:
                                continue

                            # Define absolute time of current sweep step
                            current_sweep_info["step_time"].append(
                                current_sweep_start
                                + timedelta(
                                    seconds=int(j * current_sweep_setting["step_sec"])
                                )
                            )

                            # Define Bias intensity values on the three
                            # antennas
                            current_sweep_info["step_ibias"].append(
                                [
                                    current_sweep_setting["ibias_1_def"],
                                    current_table_data[j],
                                    current_sweep_setting["ibias_3_def"],
                                ]
                            )

                            # Save progress code
                            current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                            # Define antenna flag (ANT2 = 2)
                            current_sweep_info["ant_flag"].append(ANT_2_FLAG)

                            # Define bypass values
                            current_sweep_info["bypass"].append(
                                [
                                    current_sweep_setting["bypass_1"],
                                    current_sweep_setting["bypass_2"],
                                    current_sweep_setting["bypass_3"],
                                ]
                            )

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep start on ANT3 (START_ANT3 == 5)
                # ...
                elif sweep_pr_code == 5 and is_running:
                    # Set current ant flag
                    current_ant_flag = ANT_3_FLAG

                    # Set current sweep start time (for current antenna)
                    current_sweep_start = current_time

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep step on ANT3 (STEP_ANT3 == 9) ...
                elif sweep_pr_code == 9 and is_running:
                    # Set current sweep dictionary with actual values
                    current_sweep_info["step_time"].append(current_time)
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)
                    current_sweep_info["step_ibias"].append(
                        [
                            current_sweep_setting["ibias_1_def"],
                            current_sweep_setting["ibias_2_def"],
                            raw_to_na(
                                current_packet["PA_DPU_BIA_SWEEP_VALUE"],
                                idb_version=current_idb_version,
                                idb_source=current_idb_source,
                            ).astype(float),
                        ]
                    )

                    # Save progress code
                    current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                    # Save antenna flag
                    current_sweep_info["ant_flag"].append(current_ant_flag)

                    # Save bypass values
                    current_sweep_info["bypass"].append(
                        [
                            current_sweep_setting["bypass_1"],
                            current_sweep_setting["bypass_2"],
                            current_sweep_setting["bypass_3"],
                        ]
                    )

                    # Add current sweep pr code to the list
                    current_sweep_pr_code_list.append(sweep_pr_code)

                # If event indicates a sweep end on ANT3 (END_ANT3 == 6) ...
                elif sweep_pr_code == 6 and is_running:
                    # If it is not a step-by-step sweep, then compute sweep times and intensities in nA
                    # from the latest sweep table values
                    if current_sweep_pr_code_list[-1] == 5:
                        for j in range(current_table_size):
                            # If no valid value in the table, skip current step
                            if not current_table_data[j]:
                                continue

                            # Define absolute time of current sweep step
                            current_sweep_info["step_time"].append(
                                current_sweep_start
                                + timedelta(
                                    seconds=int(j * current_sweep_setting["step_sec"])
                                )
                            )

                            # Define Bias intensity values on the three
                            # antennas
                            current_sweep_info["step_ibias"].append(
                                [
                                    current_sweep_setting["ibias_1_def"],
                                    current_sweep_setting["ibias_2_def"],
                                    current_table_data[j],
                                ]
                            )

                            # Save progress code
                            current_sweep_info["sweep_pr_code"].append(sweep_pr_code)

                            # Define antenna flag
                            current_sweep_info["ant_flag"].append(current_ant_flag)

                            # Define bypass values
                            current_sweep_info["bypass"].append(
                                [
                                    current_sweep_setting["bypass_1"],
                                    current_sweep_setting["bypass_2"],
                                    current_sweep_setting["bypass_3"],
                                ]
                            )

                    # Set sweep end time
                    current_sweep_info["end_time"] = current_time

                    # Disable is_running flag for current sweep
                    is_running = False

                    # Reset current_sweep_pr_code_list
                    current_sweep_pr_code_list = []

                    # Add current_sweep info into output list
                    sweep_info_list.append(current_sweep_info)

                else:
                    # Else skip ongoing sweep
                    logger.warning(
                        f"Current sweep is not complete "
                        f"(stopped at {current_time} "
                        f"with sweep_pr_code {sweep_pr_code}. "
                        f"Previous codes are {current_sweep_pr_code_list}), skip it "
                    )

                    # Disable is_running flag for current sweep
                    is_running = False
                    # Reset current_sweep_pr_code_list
                    current_sweep_pr_code_list = []
                    continue

        return sweep_info_list

    def load_sweep_tables(self):
        """


        :return: sweep_table_data pandas.DataFrame containing data from pipeline.event_log
        """
        sweep_table_data = None

        # First retrieve sweep table data from pipeline.event_log table
        self.filters = [self.model.label.in_(BIA_SWEEP_TABLE_PACKETS)]
        logger.debug(
            "Getting existing Bias sweep table data in pipeline.event_log table ..."
        )
        # Return existing data as a pandas.DataFrame object
        sweep_table_data = query_db(
            self.session,
            self.model,
            filters=and_(*self.filters),
            tryouts=self.tryouts,
            wait=self.wait,
            limit=self.limit,
        )
        n_data = sweep_table_data.shape[0]
        if n_data == 0:
            logger.warning("No sweep table TC found in the database")
        else:
            logger.info(f"{n_data} sweep table TCs found in the database")
            # Prepare table data to be used by L0ToL1BiaSweep task
            sweep_table_data = DbToAncBiaSweepTable.prep_sweep_table(sweep_table_data)

        return sweep_table_data
