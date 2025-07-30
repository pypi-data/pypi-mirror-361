#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Contains task to generate CSV file containing SolO S/C distance to Sun (in AU) for each date.
This file is needed by MUSIC FAUST app to define the occurrence rate of the Bias sweeps.
"""

import os
import uuid
from datetime import datetime, timedelta
from glob import glob
import csv

from poppy.core.logger import logger
from poppy.core.task import Task

from roc.rpl.time.spice import SpiceHarvester

from roc.film.tools.file_helpers import get_output_dir
from roc.film.constants import CP_START_TIME, NAIF_SPICE_ID, TIME_DAILY_STRFORMAT

__all__ = ["ExportSoloHeeCoord"]


class ExportSoloHeeCoord(Task):
    """
    Task to export SolO HEE coordinates in a CSV file
    with (distance in AU, longitude in deg, latitude in deg).
    """

    plugin_name = "roc.film"
    name = "export_solo_hee_coord"

    def add_targets(self):
        pass

    def setup_inputs(self):
        # Get/create list of well processed DDS files
        self.processed_files = self.pipeline.get(
            "processed_files", default=[], create=True
        )

        # Get/create list of failed DDS files
        self.failed_files = self.pipeline.get("failed_files", default=[], create=True)

        # If output directory not found, create it
        self.output_dir = get_output_dir(self.pipeline)
        if not os.path.isdir(self.output_dir):
            logger.debug(f"Making {self.output_dir}...")
            os.makedirs(self.output_dir)

        # Get path of SPICE kernels
        self.kernel_path = SpiceHarvester.spice_kernel_path()

        # Load SPICE kernels (only meta kernels for the moment)
        self.spice = SpiceHarvester.load_spice_kernels(
            self.kernel_path, only_mk=True, predictive=False, flown=False
        )

        # Function to convert from radians to degrees
        self.dpr = self.spice._spiceypy.dpr()

        # Define output file start time
        self.start_time = self.pipeline.get("start_time", default=[None])[0]
        logger.debug(f"start_time value is {self.start_time}")

        # Define output file end time
        self.end_time = self.pipeline.get("end_time", default=[None])[0]
        logger.debug(f"end_time value is {self.end_time}")

        # Generating list of days for which distance will be computed
        if self.start_time is None:
            self.start_time = CP_START_TIME

        if self.end_time is None:
            self.end_time = datetime.today() + timedelta(days=90)

        # Get output_csv input argument
        self.output_csv = self.pipeline.get("output_csv", default=[None])[0]
        if self.output_csv is None:
            # If not passed, then try to generate automatically the output CSV filename
            basename = f"solo_ANC_solo-hee-coord_{self.start_time.strftime(TIME_DAILY_STRFORMAT)}T{self.end_time.strftime(TIME_DAILY_STRFORMAT)}"
            pattern = os.path.join(self.output_dir, basename + "*.csv")
            existing_files = list(glob(pattern))
            data_version = f"{len(existing_files) + 1:02d}"
            self.output_csv = os.path.join(
                self.output_dir, basename + f"_V{data_version}.csv"
            )

    def run(self):
        # Define task job ID (long and short)
        self.job_id = str(uuid.uuid4())
        self.job_sid = self.job_id[:8]
        logger.info(f"[{self.job_sid}]\t Task started")
        try:
            self.setup_inputs()
        except Exception:
            logger.exception(f"[{self.job_sid}]\t Initializing inputs has failed!")
            self.pipeline.exit()
            return

        logger.info(f"Creating {self.output_csv} ...")
        with open(self.output_csv, "w", newline="") as csvfile:
            fieldnames = ["DATE", "R_AU", "HEE_LON_DEG", "HEE_LAT_DEG"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Compute SolO S/C HEE coordinates [r(AU), long(deg), lat(deg)]
            # for each day of the mission
            # and write results in the CSV file
            current_date = self.start_time.date()
            while current_date <= self.end_time.date():
                # Convert time to string then ephemeris time
                time_str = current_date.strftime("%Y %B %d") + " 12:00:00"
                et = self.spice._spiceypy.str2et(time_str)

                # Now we need to compute the actual distance between
                # the Sun and Solar Orbiter. The above spkezp call gives us
                # the apparent distance, so we need to adjust our
                # aberration correction appropriately.
                [solo_hee_pos, ltime] = self.spice._spiceypy.spkezp(
                    NAIF_SPICE_ID["SUN"],
                    et,
                    "SOLO_HEE",
                    "NONE",
                    NAIF_SPICE_ID["SOLAR_ORBITER"],
                )
                # Convert SOLO HEE coordinates to [radius, longitude, latitude]
                [r, lon, lat] = self.spice._spiceypy.reclat(solo_hee_pos)
                lat = -lat * self.dpr
                lon = 180.0 + (lon * self.dpr) if lon <= 0 else (lon * self.dpr) - 180.0

                # Convert radius to AU using convrt.
                r_au = self.spice._spiceypy.convrt(r, "KM", "AU")
                # print(time_str, r_au, lon, lat)

                row_to_write = {
                    "DATE": current_date.strftime(TIME_DAILY_STRFORMAT),
                    "R_AU": r_au,
                    "HEE_LON_DEG": lon,
                    "HEE_LAT_DEG": lat,
                }
                writer.writerow(row_to_write)
                logger.debug(f"New line {row_to_write} in {self.output_csv}")

                current_date += timedelta(days=1)
