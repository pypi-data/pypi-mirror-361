#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module to perform some post-processing on the RPW CDF files."""

import json
import os
import shutil
from datetime import datetime, timedelta
import itertools

from sqlalchemy import and_
import numpy as np
import uuid

import subprocess
from spacepy import pycdf

from poppy.core.db.connector import Connector
from poppy.core.logger import logger
from poppy.core.task import Task
from poppy.core.target import FileTarget

from roc.rpl.time import Time
from roc.dingo.models.data import EventLog
from roc.dingo.models.packet import TcLog
from roc.dingo.tools import query_db
from roc.dingo.constants import PIPELINE_DATABASE

from roc.film import (
    INPUT_DATETIME_STRFTIME,
)
from roc.film.tools.file_helpers import (
    is_output_dir,
    get_output_dir,
    get_files_datetime,
)
from roc.film.tools import glob_list
from roc.film.constants import (
    CDFCONVERT_PATH,
    TIMEOUT,
    CDF_POST_PRO_OPTS_ARGS,
    TIME_DAILY_STRFORMAT,
    QB_EVENT_LOG_LIST,
)
from roc.film.exceptions import L1PostProError

__all__ = ["CdfPostPro"]


class CdfPostPro(Task):
    """
    Task to post-process RPW CDFs
    """

    plugin_name = "roc.film"
    name = "cdf_post_pro"

    def add_targets(self):
        self.add_input(
            target_class=FileTarget,
            identifier="cdf_file",
            filepath=self.get_cdf_files(),
            many=True,
        )

        self.add_output(target_class=FileTarget, identifier="cdf_file", many=True)

    def get_cdf_files(self):
        try:
            return self.pipeline.args.cdf_files
        except Exception:
            pass

    @Connector.if_connected(PIPELINE_DATABASE)
    def setup_inputs(self):
        try:
            self.cdf_file_list = sorted(glob_list(self.inputs["cdf_file"].filepath))
        except Exception:
            raise ValueError('No input target "cdf_file" passed')

        if not self.cdf_file_list:
            logger.warning("Empty list of input cdf files")
            self.pipeline.exit()
            return

        # Get post-processing options
        self.options = [
            opt.lower()
            for opt in self.pipeline.get("options", default=[], args=True)
            if opt.lower() in CDF_POST_PRO_OPTS_ARGS
        ]
        if not self.options:
            raise ValueError("No valid argument passed in --options")

        # Get cdfconvert path
        self.cdfconvert = self.pipeline.get("cdfconvert", default=[CDFCONVERT_PATH])[0]
        if not self.cdfconvert or not os.path.isfile(self.cdfconvert):
            self.cdfconvert = os.path.join(
                os.getenv("CDF_BIN", os.path.dirname(CDFCONVERT_PATH)), "cdfconvert"
            )

        # get update-jon value
        self.update_json = self.pipeline.get("update_json", default=[None])[0]

        if "update_cdf" in self.options and not self.update_json:
            raise ValueError(
                '"update_cdf" input option needs '
                "a valid update_json file path to be run!"
            )
        elif "update_cdf" in self.options and self.update_json:
            # Get info in the input JSON file
            try:
                with open(self.update_json, "r") as jsonfile:
                    update_data = json.load(jsonfile)
                self.update_data = update_data["updates"]
            except Exception as e:
                logger.exception(
                    f"Cannot parsing {self.update_json}\t[{self.job_id}]\n{e}"
                )
                raise
        else:
            self.update_data = None

        # Get overwrite boolean input
        self.overwrite = self.pipeline.get("overwrite", default=False, args=True)
        # Get or create failed_files list from pipeline properties
        self.failed_files = self.pipeline.get("failed_files", default=[], create=True)

        # Get or create processed_files list from pipeline properties
        self.processed_files = self.pipeline.get(
            "processed_files", default=[], create=True
        )

        # Get products directory (folder where final output files will be
        # moved)
        self.products_dir = self.pipeline.get(
            "products_dir", default=[None], args=True
        )[0]

        # Get output dir
        self.output_dir = get_output_dir(self.pipeline)
        if not is_output_dir(self.output_dir, products_dir=self.products_dir):
            logger.debug(f"Making {self.output_dir}")
            os.makedirs(self.output_dir)
        elif not self.overwrite:
            logger.info(
                f"Output files will be saved into existing folder {self.output_dir}"
            )

        # Get (optional) arguments for SPICE
        self.predictive = self.pipeline.get("predictive", default=False, args=True)
        self.kernel_date = self.pipeline.get("kernel_date", default=None, args=True)
        self.no_spice = self.pipeline.get("no_spice", default=False, args=True)
        # Get/create Time singleton
        self.time_instance = Time(
            predictive=self.predictive,
            kernel_date=self.kernel_date,
            no_spice=self.no_spice,
        )

        # Get time range of the input files
        files_datetimes = get_files_datetime(self.cdf_file_list)
        files_datetimes = sorted(list(itertools.chain.from_iterable(files_datetimes)))
        self.time_range = [files_datetimes[0], files_datetimes[-1]]

        # get a database session
        self.session = Connector.manager[PIPELINE_DATABASE].session

        # Initialize some class variables
        self.obs_id_list = []
        self.event_log = None

        return True

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.info(f"Task job {self.job_id} is starting")
        try:
            self.setup_inputs()
        except:  # noqa: E722
            logger.exception(f"Initializing inputs has failed for {self.job_id}!")
            self.pipeline.exit()
            return

        # Loop over each input CDF file
        logger.info(
            f"{len(self.cdf_file_list)} input CDF files "
            f"to post-process\t[{self.job_id}]"
        )
        logger.debug(f"Covered time range is {self.time_range}\t[{self.job_id}]")
        for current_file in self.cdf_file_list:
            if self.overwrite:
                # If overwrite is set, then update current file
                logger.info(f"{current_file} will be overwritten\t[{self.job_id}]")
                self.current_file = current_file
            else:
                # Otherwise create a copy of the input CDF in the output
                # directory, then update the copy
                logger.info(
                    f"Working with a copy of {current_file} in {self.output_dir}\t[{self.job_id}]"
                )
                self.current_file = os.path.join(
                    self.output_dir, os.path.basename(current_file)
                )
                shutil.copyfile(current_file, self.current_file)

            # Open CDF
            try:
                logger.debug(
                    f"Opening and updating {self.current_file}...\t[{self.job_id}]"
                )
                # Open CDF to change what can be updated in one shot
                with pycdf.CDF(self.current_file) as cdf:
                    cdf.readonly(False)

                    # Get RPW CDF dataset ID
                    self.dataset_id = cdf.attrs["Dataset_ID"][0]

                    # Get Datetime attribute value (only first 8 characters)
                    self.datetime = datetime.strptime(
                        cdf.attrs["Datetime"][0][:8], TIME_DAILY_STRFORMAT
                    )

                    # Get time range of the input L1 CDF
                    self.epoch = cdf["Epoch"][...]
                    self.nrec = self.epoch.shape[0]
                    self.time_min = min(self.epoch)
                    self.time_max = max(self.epoch)
                    logger.info(
                        f"{self.current_file} has {self.nrec} records "
                        f"between {self.time_min} "
                        f"and {self.time_max}\t[{self.job_id}]"
                    )

                    # Set OBS_ID global attribute
                    # from unique_id entries in pipeline.tc_log database table
                    if "obs_id" in self.options:
                        self._set_obs_id(cdf)

                    # Set quality_bitmask
                    if "quality_bitmask" in self.options:
                        if "QUALITY_BITMASK" in cdf:
                            self._set_bitmask(cdf)
                        else:
                            logger.debug(
                                'No "QUALITY_BITMASK" variable found'
                                f" in {self.current_file}: skip setting!\t[{self.job_id}]"
                            )

                    # Resize TDS/LFR waveform array (only for TDS/LFR RSWF/TSWF
                    # products)
                    if "resize_wf" in self.options:
                        # Only resize TDS RSWF/TSWF products
                        if "RSWF" in self.dataset_id or "TSWF" in self.dataset_id:
                            self._set_resize_wf(cdf)
                        else:
                            logger.debug(
                                "Resizing wf cannot be "
                                f"applied on {self.dataset_id}\t[{self.job_id}]"
                            )

                    # Update CDF content with information in the input update_json file
                    if "update_cdf" in self.options:
                        self._update_cdf(cdf)

                # Apply cdfconvert to rebuild CDF properly
                if "cdf_convert" in self.options:
                    try:
                        self._run_cdfconvert(self.current_file)
                    except FileNotFoundError:
                        logger.error(
                            "cdfconvert calling has failed because "
                            f"{self.current_file} has not been found\t[{self.job_id}]"
                        )
                    except subprocess.CalledProcessError as e:
                        logger.error(
                            f"cdfconvert calling has failed: \n {e}\t[{self.job_id}]"
                        )
                    except subprocess.TimeoutExpired as e:
                        logger.error(
                            f"cdfconvert calling has expired: \n {e}\t[{self.job_id}]"
                        )
                    except:  # noqa: E722
                        logger.error("cdfconvert calling has failed!\t[{self.job_id}]")

            except:  # noqa: E722
                logger.exception(
                    f"Post-processing {self.current_file} has failed\t[{self.job_id}]"
                )
                if self.current_file not in self.failed_files:
                    self.failed_files.append(self.current_file)
            else:
                if not self.overwrite and self.current_file not in self.processed_files:
                    self.processed_files.append(self.current_file)

    def _run_cdfconvert(self, cdf_file):
        """
        Run cdfconvert tool for input CDF file

        :param cdf_file: cdf file to process with cdfconvert
        :return: CompletedProcess object returned by subprocess.run()
        """

        # Check if cdfconvert tool path exists
        if not os.path.isfile(self.cdfconvert):
            raise FileNotFoundError(f"{self.cdfconvert} not found\t[{self.job_id}]")

        # Build command to run cdfconvert with subprocess.run
        cmd = list([self.cdfconvert, cdf_file, cdf_file])
        # overwrite the existing file
        cmd.append("-delete")
        # Force some CDF features
        cmd.append("-network")
        cmd.append("-single")
        cmd.append("-compressnonepoch")
        cmd.append("-checksum md5")
        cmd = " ".join(cmd)

        # run cdfexport
        logger.info(f"Running --> {cmd}\t[{self.job_id}]")
        completed = subprocess.run(cmd, shell=True, check=True, timeout=TIMEOUT)

        return completed

    def _set_resize_wf(self, cdf_obj):
        """
        Resize Waveform array in the input CDF.

        WARNING: At the end, WF arrays will be resized,
        but CDF file size will remain unchanged.
        To make sure to have the final CDF size,
        run cdf_post_pro with cdf_export option

        :param cdf_obj: CDF to update (passed as a spacepy.pycdf.CDF class instance)
        :return: True if resizing has succeeded, False otherwise
        """
        is_succeeded = True

        # pycdf.lib.set_backward(False)

        logger.info(
            f"Resizing waveform data array in {self.current_file} ...\t[{self.job_id}]"
        )
        try:
            # Get max number of data samples in the file
            max_samp_per_ch = np.max(cdf_obj["SAMPS_PER_CH"][...])

            # Loop over old CDF zVariables
            for varname in cdf_obj:
                if (
                    varname == "WAVEFORM_DATA"
                    or varname == "WAVEFORM_DATA_VOLTAGE"
                    or varname == "B"
                ):
                    old_var = cdf_obj[varname]
                    # Re-size waveform data array
                    if len(old_var.shape) == 2:
                        new_var_data = old_var[:, :max_samp_per_ch]
                        new_var_dims = [new_var_data.shape[1]]
                    elif len(old_var.shape) == 3:
                        new_var_data = old_var[:, :, :max_samp_per_ch]
                        new_var_dims = [new_var_data.shape[1], new_var_data.shape[2]]
                    else:
                        raise IndexError

                    logger.debug(
                        f"Resizing {varname} zVar "
                        f"from {old_var.shape} to {new_var_data.shape} "
                        f"in {self.current_file}\t[{self.job_id}]"
                    )

                    # Create temporary new zVar with the new shape
                    temp_varname = f"{varname}__TMP"
                    cdf_obj.new(
                        temp_varname,
                        data=new_var_data,
                        recVary=old_var.rv(),
                        dimVarys=old_var.dv(),
                        type=old_var.type(),
                        dims=new_var_dims,
                        n_elements=old_var.nelems(),
                        compress=old_var.compress()[0],
                        compress_param=old_var.compress()[1],
                    )

                    # Copy zVar attributes
                    cdf_obj[temp_varname].attrs = cdf_obj[varname].attrs

                    # Delete old zVar
                    del cdf_obj[varname]

                    # Rename temporary zVar with expected name
                    cdf_obj[temp_varname].rename(varname)

        except Exception:
            raise L1PostProError(
                f"Resizing {self.current_file} has failed!\t[{self.job_id}]"
            )
        else:
            # make sure to save the change
            cdf_obj.save()

        return is_succeeded

    def _set_obs_id(self, cdf_obj):
        """
        Set input CDF file with expected value for OBS_ID g.attribute.

        :param cdf_obj: CDF to update (passed as a spacepy.pycdf.CDF class instance)
        :return: True if OBS_ID has been set, False otherwise
        """

        logger.info(
            f"Setting OBS_ID global attribute "
            f"in {self.current_file} ...\t[{self.job_id}]"
        )

        # Get list of RPW TC obs id values
        if not self.obs_id_list:
            logger.debug(
                f"Requesting pipeline.tc_log table entries from database...\t[{self.job_id}]"
            )
            self.obs_id_list = self.get_tc_log_data()

        # Keep only obs_id between time_min and time_max
        obs_id_list = list(
            set(
                [
                    current_tc["unique_id"]
                    for current_tc in self.obs_id_list
                    if current_tc["unique_id"]
                    and self.time_max >= current_tc["utc_time"] >= self.time_min
                ]
            )
        )

        obs_id_len = len(obs_id_list)
        if obs_id_len == 0:
            logger.info(
                "No OBS_ID value found "
                f"between {self.time_min} and {self.time_max}\t[{self.job_id}]"
            )
            # Force value to "none"
            cdf_obj.attrs["OBS_ID"] = ["none"]
            return False
        else:
            cdf_obj.attrs["OBS_ID"] = sorted(list(set(obs_id_list)))
            logger.debug(f"OBS_ID = {obs_id_list} in {self.current_file}")
            logger.info(
                f"{obs_id_len} entries set for OBS_ID "
                f"in {self.current_file}\t[{self.job_id}]"
            )

        # make sure to save the change
        cdf_obj.save()

        return True

    def get_tc_log_data(self):
        """
        Return list of [unique_id, utc_time] entries from
        pipeline.tc_log database table.

        :return: tc_log data entries found
        """

        tc_log_data = query_db(
            self.session,
            [TcLog.unique_id, TcLog.utc_time],
            filters=(TcLog.tc_exe_state == "PASSED"),
            to_dict="records",
        )

        return tc_log_data

    def _update_cdf(self, cdf_obj):
        """
        Update content of input CDF

        :param cdf_obj: spacepy.pycdf.CDF object containing input file data
        :return:
        """
        is_succeeded = True

        for item in self.update_data:
            # Filter dataset to update
            if item.get("include") and self.dataset_id not in item["include"]:
                logger.debug(
                    f"Skipping {self.current_file} "
                    f"for updating CDF: {self.dataset_id} not concerned\t[{self.job_id}]"
                )
                continue

            if item.get("exclude") and self.dataset_id in item["exclude"]:
                logger.debug(
                    f"Skipping {self.current_file} "
                    f"for updating CDF: {self.dataset_id} not concerned\t[{self.job_id}]"
                )
                continue

            # Retrieve validity time ranges
            validity_start = datetime.strptime(
                item["validity_range"]["start_time"], INPUT_DATETIME_STRFTIME
            )
            validity_end = datetime.strptime(
                item["validity_range"]["end_time"], INPUT_DATETIME_STRFTIME
            )
            # Filter time range
            if self.datetime.date() < validity_start.date():
                logger.debug(
                    f"Skipping {self.current_file} "
                    f"for updating CDF: older than {validity_start.date()}\t[{self.job_id}]"
                )
                continue

            if self.datetime.date() > validity_end.date():
                logger.debug(
                    f"Skipping {self.current_file} for updating CDF: "
                    f"newer than {validity_end.date()}\t[{self.job_id}]"
                )
                continue

            # Update global attributes if any
            for gattr in item["gattrs"]:
                gname = gattr["name"]
                try:
                    gvalues = list(set(cdf_obj.attrs[gname][...] + gattr["values"]))
                    cdf_obj.attrs[gname] = gvalues
                except Exception as e:
                    logger.exception(
                        f"Cannot update global attribute {gname} "
                        f"in {self.current_file}\t[{self.job_id}]"
                    )
                    logger.debug(e)
                    is_succeeded = False
                else:
                    logger.info(
                        f"Global attribute {gname} updated in "
                        f"{self.current_file} with values {gvalues}\t[{self.job_id}]"
                    )

            # Update zVariables if any
            where_dt = (validity_start <= self.epoch) & (self.epoch <= validity_end)
            if any(where_dt):
                for zvar in item["zvars"]:
                    zname = zvar["name"]
                    new_zvalues = cdf_obj[zname][...]
                    new_zvalues[where_dt] = zvar["value"]
                    try:
                        cdf_obj[zname] = new_zvalues
                    except Exception as e:
                        logger.exception(
                            f"Cannot update zVariable {zname} "
                            f"in {self.current_file}\t[{self.job_id}]"
                        )
                        logger.debug(e)
                        is_succeeded = False
                    else:
                        logger.info(
                            f"{zname} updated "
                            f"in {self.current_file} with value {zvar['value']}\t[{self.job_id}]"
                        )

        # make sure to save the change
        cdf_obj.save()

        return is_succeeded

    def _set_bitmask(self, cdf_obj):
        """
        Set the QUALITY_BITMASK zVariable in RPW L1 CDF.
        See https://confluence-lesia.obspm.fr/display/ROC/RPW+Data+Quality+Verification

        :param cdf_obj: spacepy.pycdf.CDF object containing input file data
        :return: None
        """
        logger.info(
            f"Setting QUALITY_BITMASK zVar in {self.current_file}...\t[{self.job_id}]"
        )
        # Restore Epoch values and get number of records in CDF
        epoch = self.epoch
        nrec = self.nrec

        # Initialize quality_bitmask
        bitmask = np.zeros(nrec, dtype=np.uint16)

        # Get list of events to store in bitmask between time_min and time_max
        # Define filters
        if self.event_log is None:
            logger.debug(f"Querying event_log table...\t[{self.job_id}]")
            model = EventLog
            filters = [
                model.start_time >= self.time_range[0] - timedelta(days=1),
                model.end_time <= self.time_range[1] + timedelta(days=1),
                model.label.in_(QB_EVENT_LOG_LIST),
            ]
            self.event_log = query_db(
                self.session,
                model,
                filters=and_(*filters),
            )

        n_event = self.event_log.shape[0]
        if n_event == 0:
            logger.warning(
                f"No event_log entry found "
                f"between {self.time_min} and {self.time_max}\t[{self.job_id}]"
            )
        else:
            logger.debug(
                f"{n_event} entries found in event_log table...\t[{self.job_id}]"
            )
            # Loop over events to fill quality_bitmask
            for i, row in self.event_log.iterrows():
                # Filter events
                if row["label"] not in QB_EVENT_LOG_LIST:
                    logger.exception(
                        f"{row['label']} is not in the list {QB_EVENT_LOG_LIST}"
                    )
                    raise ValueError

                # Check that CDF time range covering the event
                if row["start_time"] > self.time_max or row["end_time"] < self.time_min:
                    # If not, skip next steps
                    continue

                # Get Epoch indices associated to the time range covering the event
                w = (row["start_time"] <= epoch) & (row["end_time"] >= epoch)
                if not any(w):
                    continue

                # BIAS SWEEP on ANT1
                if row["label"] == "BIA_SWEEP_ANT1":
                    # Set 1st bit (X)
                    bitmask[w] = bitmask[w] | 1

                # BIAS SWEEP on ANT2
                elif row["label"] == "BIA_SWEEP_ANT2":
                    # Set 2nd bit (X0)
                    bitmask[w] = bitmask[w] | 2

                # BIAS SWEEP on ANT3
                elif row["label"] == "BIA_SWEEP_ANT3":
                    # Set 3rd bit (X00)
                    bitmask[w] = bitmask[w] | 4

                # EMC_MAND_QUIET
                elif row["label"] == "EMC_MAND_QUIET":
                    # Set 4th bit (X000)
                    bitmask[w] = bitmask[w] | 8

                # EMC_PREF_NOISY
                elif row["label"] == "EMC_PREF_NOISY":
                    # Set 5th bit (X0000)
                    bitmask[w] = bitmask[w] | 16

                # Spacecraft roll manoeuvre
                elif "ROLL" in row["label"]:
                    # Set 6th bit (X00000)
                    bitmask[w] = bitmask[w] | 32

                # Spacecraft "slew" roll manoeuvre
                elif "SLEW" in row["label"]:
                    # Set 6th bit (X00000)
                    bitmask[w] = bitmask[w] | 32

                # Thruster firing
                elif row["label"] in ["TCM", "WOL"]:
                    # Set 7th bit (X000000)
                    bitmask[w] = bitmask[w] | 64

                logger.debug(
                    f"Set {len(w)} QUALITY_BITMASK records for {row['label']} "
                    f"between {row['start_time']} "
                    f"and {row['end_time']}\t[{self.job_id}]"
                )

        # Save quality_bitmask
        cdf_obj["QUALITY_BITMASK"] = bitmask[...]

        # make sure to save the change
        cdf_obj.save()

        return True


def cast_ior_seq_datetime(current_seq, strtformat):
    """
    cast the execution time of the input IOR sequence element into datetime object
    """
    try:
        seq_datetime = datetime.strptime(
            current_seq["executionTime"]["actionTime"], strtformat
        )
    except Exception:
        # logger.debug(e)
        seq_datetime = None

    return seq_datetime
