#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
from os import path as osp
from datetime import datetime

from poppy.core.conf import settings
from poppy.core.logger import logger

__all__ = [
    "PLUGIN",
    "PIPELINE_DATABASE",
    "INPUT_DATETIME_STRFTIME",
    "TIME_ISO_STRFORMAT",
    "TIME_DAILY_STRFORMAT",
    "CDF_TRANGE_STRFORMAT",
    "TIME_GEN_STRFORMAT",
    "TIME_JSON_STRFORMAT",
    "TIME_L0_STRFORMAT",
    "TIME_DOY1_STRFORMAT",
    "TIME_DOY2_STRFORMAT",
    "SCOS_HEADER_BYTES",
    "DATA_VERSION",
    "UNKNOWN_IDB",
    "CHUNK_SIZE",
    "TC_ACK_ALLOWED_STATUS",
    "TEMP_DIR",
    "ARCHIVE_DAILY_DIR",
    "TMRAW_PREFIX_BASENAME",
    "TCREPORT_PREFIX_BASENAME",
    "TC_ACK_ALLOWED_STATUS",
    "ANT_1_FLAG",
    "ANT_2_FLAG",
    "ANT_3_FLAG",
    "TM_PACKET_CATEG",
    "MIN_DATETIME",
    "MAX_DATETIME",
    "PACKET_TYPE",
    "CDFCONVERT_PATH",
    "TIMEOUT",
    "CDF_POST_PRO_OPTS_ARGS",
    "BIA_SWEEP_TABLE_NR",
    "CP_START_TIME",
    "SOLO_START_TIME",
    "SOLO_END_TIME",
    "NAIF_SPICE_ID",
    "TRYOUTS",
    "TIME_WAIT_SEC",
    "SQL_LIMIT",
    "BIA_SWEEP_TABLE_PACKETS",
    "QB_EVENT_LOG_LIST",
]

# root directory of the module
_ROOT_DIRECTORY = osp.abspath(
    osp.join(
        osp.dirname(__file__),
    )
)

# Name of the plugin
PLUGIN = "roc.film"

# Load pipeline database identifier
try:
    PIPELINE_DATABASE = settings.PIPELINE_DATABASE
except AttributeError:
    PIPELINE_DATABASE = "PIPELINE_DATABASE"
    logger.warning(
        f'settings.PIPELINE_DATABASE not defined for {__file__}, use "{PIPELINE_DATABASE}" by default!'
    )

# STRING format for time
INPUT_DATETIME_STRFTIME = "%Y-%m-%dT%H:%M:%S"
TIME_ISO_STRFORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
TIME_DAILY_STRFORMAT = "%Y%m%d"
CDF_TRANGE_STRFORMAT = "%Y%m%dT%H%M%S"
TIME_GEN_STRFORMAT = "%Y-%m-%dT%H:%M:%S.%f"
TIME_JSON_STRFORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_L0_STRFORMAT = "%Y-%m-%dT%H:%M:%S.%f000Z"
TIME_DOY1_STRFORMAT = "%Y-%jT%H:%M:%S.%fZ"
TIME_DOY2_STRFORMAT = "%Y-%jT%H:%M:%SZ"

# Datetime values min/max range
MIN_DATETIME = datetime(1999, 1, 1)
MAX_DATETIME = datetime(2100, 12, 31)

# SolO mission start/end time
SOLO_START_TIME = datetime(2020, 2, 10)
SOLO_END_TIME = datetime(2029, 6, 1)

# Cruise Phase start time
CP_START_TIME = datetime(2020, 6, 15)

# Relative output directory path of the RPW file local archive
ARCHIVE_DAILY_DIR = "%Y/%m/%d"

# TmRaw prefix basename
TMRAW_PREFIX_BASENAME = "solo_TM_rpw"

# TcReport prefix basename
TCREPORT_PREFIX_BASENAME = "solo_TC_rpw"

# SOLO HK prefix basename
SOLOHK_PREFIX_BASENAME = "solo_HK_platform"

# DDS TmRaw SCOS header length in bytes
SCOS_HEADER_BYTES = 76

# Default value for data_version
DATA_VERSION = "01"

# Default IDB source/version values
UNKNOWN_IDB = "UNKNOWN"

# Temporary dir
TEMP_DIR = tempfile.gettempdir()

# Number of packets/events to be processed at the same time
CHUNK_SIZE = 10000

# TC Packet ack possible status in L0 files
TC_ACK_ALLOWED_STATUS = ["PASSED", "FAILED"]

# Antenna flags
ANT_1_FLAG = 1
ANT_2_FLAG = 2
ANT_3_FLAG = 3

# Packet category list
TM_PACKET_CATEG = ["ev", "hk", "oth", "ll", "sci", "sbm"]

# Packet type list
PACKET_TYPE = ["TM", "TC"]

# Path to the cdfconvert executable (default)
CDFCONVERT_PATH = "/pipeline/lib/cdf/current/bin/cdfconvert"

# Max process timeout
TIMEOUT = 14400

# Allowed values for keyword --options in l1_post_pro command
CDF_POST_PRO_OPTS_ARGS = [
    "obs_id",
    "resize_wf",
    "update_cdf",
    "quality_bitmask",
    "cdf_convert",
]

# Number of max. values that can be stored in the bias sweep table
BIA_SWEEP_TABLE_NR = 256

# List of NAIF SPICE IDs
NAIF_SPICE_ID = {
    "SUN": 10,
    "SOLAR_ORBITER": -144,
}

# Number of database connexion tryouts
TRYOUTS = 3

# Time to wait in seconds between two database connection tryouts
TIME_WAIT_SEC = 3

# Limit of rows to be returned by the database
SQL_LIMIT = 1000000000

# Names of TC handling Bias sweep table
BIA_SWEEP_TABLE_PACKETS = ["TC_DPU_LOAD_BIAS_SWEEP", "TC_DPU_CLEAR_BIAS_SWEEP"]

# List of events to query for setting quality_bitmask in cdf_postpro task
QB_EVENT_LOG_LIST = [
    "BIA_SWEEP_ANT1",
    "BIA_SWEEP_ANT2",
    "BIA_SWEEP_ANT3",
    "EMC_MAND_QUIET",
    "EMC_PREF_NOISY",
    "TCM",
    "SLEW",
    "WOL",
    "ROLL",
]
