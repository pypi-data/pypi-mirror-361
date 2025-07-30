#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Contains task to create the RPW ANC Bias sweep table CDF files."""

import csv
import os
import uuid
from datetime import datetime
import pandas as pd
from sqlalchemy import and_

from poppy.core.logger import logger
from poppy.core import TargetFileNotSaved
from poppy.core.db.connector import Connector
from poppy.core.generic.cache import CachedProperty
from poppy.core.target import FileTarget
from poppy.core.task import Task

from roc.dingo.models.data import EventLog
from roc.dingo.tools import valid_time, query_db, get_columns

from roc.film import TIME_DAILY_STRFORMAT, TIME_ISO_STRFORMAT
from roc.film.constants import (
    PIPELINE_DATABASE,
    TRYOUTS,
    SQL_LIMIT,
    TIME_WAIT_SEC,
    BIA_SWEEP_TABLE_PACKETS,
)
from roc.film.tools import get_datasets
from roc.film.tools.file_helpers import get_output_dir, is_output_dir, generate_filepath
from roc.film.tools.metadata import set_logical_file_id

__all__ = ["DbToAncBiaSweepTable"]


class DbToAncBiaSweepTable(Task):
    """
    Task to generate ANC bias sweep table file from pipeline.event_log table data.

    For more information about the Bias sweeping, see section 'BIAS sweeping' of
    the RPW DAS User Manual (RPW-SYS-MEB-DPS-NTT-000859-LES)

    """

    plugin_name = "roc.film"
    name = "db_to_anc_bia_sweep_table"

    csv_fieldnames = [
        "TC_EXE_UTC_TIME",
        "BIA_SWEEP_TABLE_CUR",
        "EEPROM_LOADING",
        "TC_NAME",
        "TC_EXE_STATE",
    ]

    def add_targets(self):
        self.add_output(target_class=FileTarget, identifier="anc_bia_sweep_table")

    def setup_inputs(self):
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

        # Get or create failed_files list from pipeline properties
        self.failed_files = self.pipeline.get("failed_files", default=[], create=True)

        # Get or create processed_files list from pipeline properties
        self.processed_files = self.pipeline.get(
            "processed_files", default=[], create=True
        )

        # Get or create ignored_target list from pipeline properties
        self.ignored_target = self.pipeline.get(
            "ignored_target", default=[], create=True
        )

        # Get overwrite argument
        self.overwrite = self.pipeline.get("overwrite", default=False, args=True)

        # Get force optional keyword
        self.force = self.pipeline.get("force", default=False, args=True)

        # Retrieve output dataset to produce for the task (it should be one)
        self.dataset = get_datasets(self, self.name)[0]
        logger.debug(
            f"Produce file(s) for the following dataset: {self.dataset['name']}"
        )

        # Get start_time input value
        self.start_time = valid_time(
            self.pipeline.get("start_time", default=[None])[0],
            str_format=TIME_DAILY_STRFORMAT,
        )

        # Get end_time input value
        self.end_time = valid_time(
            self.pipeline.get("end_time", default=[None])[0],
            str_format=TIME_DAILY_STRFORMAT,
        )

        # Define query filters for existing data in database
        self.filters = []
        if self.start_time:
            self.filters.append(self.model.start_time >= str(self.start_time))
        if self.end_time:
            self.filters.append(self.model.end_time < str(self.end_time))

        return True

    @CachedProperty
    def output_filepath(self):
        # Build output filename using metadata
        filename_items = {}
        filename_items["File_naming_convention"] = (
            "<Source_name>_<LEVEL>_<Descriptor>_<Datetime>_V<Data_version>"
        )
        filename_items["Source_name"] = "SOLO>Solar Orbiter"
        filename_items["Descriptor"] = "RPW-BIA-SWEEP-TABLE>RPW Bias sweep table report"
        filename_items["LEVEL"] = "ANC>Ancillary data"
        filename_items["Data_version"] = self.dataset["version"]

        filename_items["Datetime"] = (
            self.start_time.strftime(TIME_DAILY_STRFORMAT)
            + "-"
            + self.end_time.strftime(TIME_DAILY_STRFORMAT)
        )
        filename_items["Logical_file_id"] = set_logical_file_id(filename_items)
        return generate_filepath(
            self,
            filename_items,
            "csv",
            output_dir=self.output_dir,
            overwrite=self.overwrite,
        )

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = f"{self.job_uuid[:8]}"
        logger.info(f"Task {self.job_id} is starting")
        try:
            self.setup_inputs()
        except Exception:
            logger.exception(f"Initializing inputs has failed for {self.job_id}!")
            try:
                os.makedirs(os.path.join(self.output_dir, "failed"))
            except Exception:
                logger.error("output_dir argument is not defined!")
            self.pipeline.exit()
            return

        # First retrieve sweep table data from pipeline.event_log table
        self.filters.append(self.model.label.in_(BIA_SWEEP_TABLE_PACKETS))
        logger.debug(
            f"Getting existing event_log data between {self.start_time} and {self.end_time}"
        )
        # Return existing data as a pandas.DataFrame object
        table_data = query_db(
            self.session,
            self.model,
            filters=and_(*self.filters),
            tryouts=self.tryouts,
            wait=self.wait,
            limit=self.limit,
        )
        n_data = table_data.shape[0]
        if n_data == 0:
            logger.warning("No sweep table TC found in the database")
            return
        else:
            logger.info(f"{n_data} sweep table TCs found in the database")
            # Prepare table data to be saved in the CSV file
            table_data = DbToAncBiaSweepTable.prep_sweep_table(table_data)

            # Convert current list to string values separated by ;
            table_data["BIA_SWEEP_TABLE_CUR"] = table_data["BIA_SWEEP_TABLE_CUR"].apply(
                lambda x: na_to_str(x)
            )

        if not self.start_time:
            self.start_time = table_data["TC_EXE_UTC_TIME"].min()
            self.end_time = table_data["TC_EXE_UTC_TIME"].max()

        # Write output CSV file
        output_filepath = self.output_filepath
        logger.info(f"Writing {output_filepath}...")
        try:
            with open(output_filepath, "w", newline="") as csvfile:
                table_data.to_csv(csvfile, sep=",")
        except Exception:
            if output_filepath not in self.failed_files:
                self.failed_files.append(output_filepath)
            raise TargetFileNotSaved(
                "Anc Bias sweep table csv file production has failed!"
            )

        if not os.path.isfile(output_filepath):
            if output_filepath not in self.failed_files:
                self.failed_files.append(output_filepath)
            raise FileNotFoundError(f"{output_filepath} not found")
        else:
            logger.info(f"{output_filepath} saved")
            if output_filepath not in self.processed_files:
                self.processed_files.append(output_filepath)

        self.outputs["anc_bia_sweep_table"] = output_filepath

    @staticmethod
    def parse_bia_sweep_table_file(sweep_table_file):
        """
        Parse an input bia sweep table CSV file

        :param sweep_table_file: File to parse
        :return: list of sweep tables
        """

        # Initialize output list
        sweep_table_list = []

        if not os.path.isfile(sweep_table_file):
            logger.error(f"{sweep_table_file} not found!")
        else:
            # Read file and store in output list
            with open(sweep_table_file, "r", newline="") as csv_file:
                reader = csv.DictReader(csv_file)

                # Loop over rows
                for row in reader:
                    row["TC_EXE_UTC_TIME"] = datetime.strptime(
                        row["TC_EXE_UTC_TIME"], TIME_ISO_STRFORMAT
                    )
                    row["BIA_SWEEP_TABLE_CUR"] = row["BIA_SWEEP_TABLE_CUR"].split(";")
                    sweep_table_list.append(row)

        return sweep_table_list

    @staticmethod
    def get_latest_sweep_table(current_time, sweep_table_list):
        """
        Get the latest sweep table for a given datetime

        :param current_time: Time for which sweep table must be returned (datetime object)
        :param sweep_table_list: list of sweep tables (pandas.DataFrame)
        :return: row of the sweep table list
        """

        w = (sweep_table_list["TC_EXE_STATE"] == "PASSED") & (
            sweep_table_list["TC_EXE_UTC_TIME"] <= current_time
        )
        output_table = sweep_table_list[w]

        if output_table.shape[0] > 0:
            output_table = output_table.iloc[-1]

        return output_table

    @staticmethod
    def prep_sweep_table(table_data):
        """
        Preprocess sweep table data coming from pipeline.event_log
        to be compatible with output CSV content

        :param table_data:  Sweep table data
                            extracted from event_log table
                            (Pandas.DataFrame object as returned by query_db())
        :return: modified table_data
        """
        n_data = table_data.shape[0]
        # First, sort by ascending start_time
        table_data.sort_values(by=["start_time"], inplace=True, ignore_index=True)

        # rename some columns
        table_data.rename(
            columns={
                "start_time": "TC_EXE_UTC_TIME",
                "label": "TC_NAME",
            },
            inplace=True,
        )

        # add columns for TC_EXE_STATE, EEPROM_LOADING and BIA_SWEEP_TABLE_CUR
        new_data = {
            "TC_EXE_STATE": ["PASSED"] * n_data,
            "EEPROM_LOADING": [
                int(row["sweep_eeprom"] is True) for row in table_data["description"]
            ],
            "BIA_SWEEP_TABLE_CUR": [
                row["sweep_step_na"] for row in table_data["description"]
            ],
        }
        table_data = pd.concat([table_data, pd.DataFrame.from_dict(new_data)], axis=1)

        # delete unwanted columns
        for table_col in [
            "id",
            "end_time",
            "is_predictive",
            "description",
            "insert_time",
        ]:
            del table_data[table_col]

        # Convert current values from string to float
        table_data["BIA_SWEEP_TABLE_CUR"] = table_data["BIA_SWEEP_TABLE_CUR"].apply(
            str_to_float
        )

        return table_data


def na_to_str(bia_current):
    """

    :param bia_current:
    :return:
    """
    if not bia_current:
        return ""
    else:
        return ";".join([str(current) for current in bia_current])


def str_to_float(str_values):
    """
    Convert string(s) to float(s)
    (with some extra rules)

    :param str_values: string value(s) to convert
    :return: converted float value(s)
    """
    if not str_values:
        return None

    is_list = isinstance(str_values, list)
    if not is_list:
        out_values = [str_values]
    else:
        out_values = str_values

    for i, out_value in enumerate(out_values):
        if out_value:
            if out_value == "nan":
                out_values[i] = None
            else:
                out_values[i] = float(out_value)
        else:
            out_values[i] = None

    if not is_list:
        out_values = out_values[0]

    return out_values
