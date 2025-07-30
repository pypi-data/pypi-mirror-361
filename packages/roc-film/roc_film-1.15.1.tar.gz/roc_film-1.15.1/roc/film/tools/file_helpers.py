#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from glob import glob
from datetime import datetime, timedelta
import uuid
import calendar
from typing import List, Union
from pathlib import Path

import h5py
import numpy as np
from spacepy.pycdf import CDF

from poppy.core import MissingArgument
from poppy.core.logger import logger
from poppy.core.task import Task
from poppy.core.pipeline import Pipeline

from roc.rpl.time import Time

# Import methods to extract data from RPW packets
from roc.film.tools.dataset_tasks import dataset_func

from roc.rap.tasks.utils import order_by_increasing_time

from roc.film.tools.metadata import (
    init_cdf_global,
    set_logical_file_id,
    get_spice_kernels,
)
from roc.film.exceptions import (
    UnknownPipeline,
    LoadDataSetError,
    NoData,
)
from roc.film.tools import valid_data_version, get_datasets, extract_datetime
from roc.film.constants import (
    TIME_ISO_STRFORMAT,
    CDF_TRANGE_STRFORMAT,
    TIME_DAILY_STRFORMAT,
    INPUT_DATETIME_STRFTIME,
)

# Import methods to extract data from RPW packets

__all__ = [
    "build_file_basename",
    "generate_filepath",
    "put_cdf_global",
    "is_packet",
    "put_cdf_zvars",
    "l0_to_trange_cdf",
    "get_l0_file",
    "get_l0_files",
    "get_output_dir",
    "get_products_dir",
    "get_master_cdf_dir",
    "is_output_dir",
    "get_files_datetime",
]


def build_file_basename(metadata: dict, is_cdag: bool = False) -> str:
    """
    "Build Solar Orbiter convention basename (without extension)
    using metadata.

        See SOL-SGS-TN-0009 for more details about SolO data standards.

    :param metadata: dictionary contains output metadata used to build filename
    :type metadata: dict
    :param is_cdag: If True, add a '-cdag' suffix to the descriptor field of the filename
    :type is_cdag: bool
    :return: RPW file basename
    :rtype: str
    """

    # if Logical_file_id attribute exists, it should contain
    # the file name without the extension
    if not is_cdag and "Logical_file_id" in metadata:
        return str(metadata["Logical_file_id"])

    # Add -cdag suffix if input is_cdag=True
    if not is_cdag:
        cdag_suffix = ""
    else:
        cdag_suffix = "-cdag"

    # Else build the file basename from scratch
    # file basename mandatory fields
    fields = [
        str(metadata["Source_name"]).split(">")[0].lower(),
        str(metadata["LEVEL"]).split(">")[0],
        str(metadata["Descriptor"]).split(">")[0].lower() + cdag_suffix,
        str(metadata["Datetime"]),
        "V" + str(metadata["Data_version"]),
    ]

    # Add free_field at the end of the file basename if it exists
    free_field = metadata.get("Free_field", "")
    if free_field and str(free_field).lower().strip() not in ["none", ""]:
        fields.append(str(metadata["Free_field"]))

    return "_".join(fields)


def generate_filepath(
    task: type[Task],
    metadata: dict,
    extension: str,
    output_dir: str = None,
    is_cdag: bool = False,
    overwrite: bool = False,
) -> str:
    """
    Generate output filepath from input task and metadata info

    :param task: pipeline task object
    :param metadata: dictionary with metadata (at least Logical_file_id and Data_version)
    :param extension: output file extension (e.g., '.cdf', '.h5')
    :param output_dir: Directory path of the output file. (If not passed, then try to get it from pipeline properties)
    :param is_cdag: If True, add a '-cdag' suffix in the descriptor of the filename
    :param overwrite: If True, overwrite existing file
    :return: Output file path
    :rtype: str
    """

    # Add dot '.' to the extension if not provided
    if not extension.startswith("."):
        extension = "." + extension

    # Build output filepath from pipeline task properties, metadata
    # and extension
    filename = build_file_basename(metadata, is_cdag=is_cdag) + extension

    if not output_dir:
        output_dir = get_output_dir(task.pipeline)
    filepath = os.path.join(output_dir, filename)

    # check if the file to generate is already existing, and remove it
    # if --overwrite input keyword is set
    if os.path.isfile(filepath) and overwrite:
        logger.warning(f"Existing {filepath} will be overwritten!")
        os.remove(filepath)
    elif os.path.isfile(filepath):
        logger.info(
            f"{filepath} already exists, create a new version of the data file."
        )
        # Else, if the output file already exists, create a new
        # version of the file (i.e., increment the data_version)

        # Get file basename (without version and extension)
        data_version = metadata["Data_version"]
        basename = os.path.basename(filename).split(f"_V{data_version}")[0]

        # Check number of files in the output directory which have the
        # same basename
        pattern = os.path.join(output_dir, basename + "*" + extension)
        file_number = len(glob(pattern))

        # Increment the data_version
        metadata["Data_version"] = valid_data_version(file_number + 1)

        # Update Logical_file_id
        metadata["Logical_file_id"] = set_logical_file_id(metadata)

        # Update filepath
        filename = build_file_basename(metadata, is_cdag=is_cdag) + extension
        output_dir = get_output_dir(task.pipeline)
        filepath = os.path.join(output_dir, filename)
        logger.debug(f"New file version V{metadata['Data_version']} has been defined")

    logger.debug(f'Output file basename has been generated from metadata: "{filename}"')

    return filepath


def get_l0_file(pipeline) -> str:
    try:
        return pipeline.args.l0_file[0]
    except:  # noqa: E722
        # If not defined as input argument, then assume that it is already
        # defined as target input
        pass


def get_l0_files(pipeline: Pipeline) -> list:
    try:
        l0_files = pipeline.args.l0_files
        if not isinstance(l0_files, list):
            l0_files = [l0_files]
        return l0_files
    except:  # noqa: E722
        # If not defined as input argument, then assume that it is already
        # defined as target input
        pass


def put_cdf_global(cdf: CDF, metadata: dict) -> bool:
    """
    Write the global attributes into the input CDF.

    :param cdf: input CDF object
    :type cdf: spacepy.pycdf.CDF
    :param metadata: Global attributes to save in the CDF
    :type metadata: dict
    :return: True, if succeeded, else raise an exception
    :rtype: bool
    """

    for key, value in metadata.items():
        if key not in cdf.attrs:
            logger.debug(f"{key} global attribute not found in CDF: force insertion!")
        cdf.attrs[key] = value

    return True


def get_files_datetime(
    list_of_files: Union[List[str], List[Path]],
) -> List[List[datetime]]:
    """
    Get the timerange of a list of input files.
    Names of the files must be compliant with SolO file naming conventions.

    :param list_of_files: Files to process
    :return: timeranges of input files
    """
    # Initialize output
    file_datetimes = []
    for current_file in list_of_files:
        # Extract date and time of input files and convert it into datetime object
        file_date = Path(current_file).stem.split("_")[3]
        if "T" in file_date:
            str_tformat = "%Y%m%dT%H%M%S"
        else:
            str_tformat = "%Y%m%d"

        file_datetimes.append(extract_datetime(file_date, str_tformat=str_tformat))

    return file_datetimes


def get_master_cdf_dir(task: type[Task]) -> str:
    """
    Try to load the master_dir directory from :
        1. the input argument --master-cdf-dir
        2. the config.json file
        3. the OS environment
    If it does not exist, set to ".".

    :param task: Poppy pipeline task instance
    :type task: Task
    :return: Master CDF directory
    :rtype: str
    """
    master_cdf_dir = task.pipeline.get("master_cdf_dir", default=None)

    if master_cdf_dir is None:
        # 2. Else from the config.json
        if (
            "RPW_CDF_MASTER_PATH"
            in task.pipeline.properties.configuration["environment"]
        ):
            master_cdf_dir = task.pipeline.properties.configuration[
                "environment.RPW_CDF_MASTER_PATH"
            ]
        # 3. Else from the OS environment
        elif "RPW_CDF_MASTER_PATH" in os.environ:
            master_cdf_dir = os.environ["RPW_CDF_MASTER_PATH"]
        # Otherwise raise an exception
        else:
            raise MissingArgument("No value found for master_cdf_dir!")
    else:
        master_cdf_dir = master_cdf_dir[0]

    return master_cdf_dir


def get_output_dir(pipeline: Pipeline) -> str:
    """
    Generate the output directory from the information provided in the
    pipeline properties and metadata.

    :param pipeline: POPPy pipeline instance
    :type pipeline: Poppy Task class
    :return: output_dir
    :rtype: str
    """

    # get pipeline id (can be "RGTS" or "RODP")
    pipeline_id = pipeline.properties.configuration["environment.ROC_PIP_NAME"]

    # Case for the ROC Ground Test SGSE (RGTS)
    if pipeline_id == "RGTS":
        # Generate output directory for current test
        try:
            output_dir = pipeline.args.test_log.output_directory(pipeline)
        except Exception as e:
            logger.debug(e)
            output_dir = pipeline.output

    # Case for the RPW Operation and Data Pipeline (RODP)
    elif pipeline_id == "RODP":
        # First get the input LZ File object from the properties
        try:
            output_dir = pipeline.output
        except Exception:
            logger.error("NO OUTPUT DIRECTORY DEFINED, ABORTING!")
            raise
    else:
        raise UnknownPipeline(f"UNKNOWN PIPELINE TYPE: {pipeline_id}, ABORTING!")

    return output_dir


def get_products_dir(pipeline: Pipeline) -> str:
    """
    Get the path of the directory where final products must be moved.

    :param pipeline: POPPy pipeline instance
    :type pipeline: Poppy Pipeline class
    :return: string containing the products directory path
    :rtype: str
    """
    products_dir = pipeline.get("products_dir", default=None, args=True)

    if products_dir is None:
        # 2. Else from the config.json
        if "ROC_PRODUCTS_PATH" in pipeline.properties.configuration["environment"]:
            products_dir = pipeline.properties.configuration[
                "environment.ROC_PRODUCTS_PATH"
            ]
        # 3. Else from the OS environment
        elif "ROC_PRODUCTS_PATH" in os.environ:
            products_dir = os.environ["ROC_PRODUCTS_PATH"]
        # Otherwise return "."
        else:
            products_dir = None
    else:
        products_dir = products_dir[0]

    return products_dir


def is_output_dir(output_dir: str, products_dir: str = None) -> bool:
    """
    Check if the output directory exists and if its basename is found in the
    products_dir.

    :param output_dir: String containing output directory
    :type output_dir: str
    :param products_dir: String containing products directory
                        (if provided, check if output_dir basename
                        is already saved inside)
    :type products_dir: str
    :return: True if output_dir is found, False otherwise
    :rtype: bool
    """

    # Get output_dir value
    if output_dir:
        output_dir_basename = os.path.basename(output_dir)
    else:
        raise MissingArgument("Output directory is not defined!")

    # Check if output_dir already exists
    if os.path.isdir(output_dir):
        logger.debug(f"{output_dir} already created")
        return True

    # Check products_dir
    if products_dir:
        # Build target directory path
        target_dir = os.path.join(products_dir, os.path.basename(output_dir))
        if os.path.isdir(target_dir):
            logger.debug(f"{output_dir_basename} already found in {products_dir}")
            return True
    else:
        logger.debug("Input argument 'products_dir' is not defined")

    return False


def is_packet(expected_packets: list, packets: list) -> bool:
    """
    Check if packet(s) is/are in the input packet_list

    :param expected_packets: Name of the packet(s) expected for the dataset
    :type expected_packets: list
    :param packets: Input packet(s) provided as a h5 group
    :type packets: list
    :return: True if at least one expected packet found, False if all expected packets not found
    :rtype: bool
    """

    if not isinstance(expected_packets, list):
        expected_packets = [expected_packets]

    for expected_packet in expected_packets:
        # If at least one expected packet is found then ...
        if expected_packet in packets.keys():
            return True

    return False


def put_cdf_zvars(
    cdf: CDF, data: np.ndarray, start_time: datetime = None, end_time: datetime = None
) -> tuple:
    """
    Write input data into CDF zVariable

    :param cdf: pycdf.CDF object to update
    :type cdf: spacepy.pycdf.CDF
    :param data: zVariable data to write into the CDF
    :type data: np.ndarray
    :param start_time: only store data after start_time
    :type start_time: datetime
    :param end_time: only store date before end_time
    :type end_time: datetime
    :return: time_min, time_max and nrec:
    :rtype: tuple
    """

    # check size of the data
    nrec = data.shape[0]
    if nrec == 0:
        raise NoData(
            message="Data for {0} is empty".format(cdf.pathname), ll=logger.warning
        )

    # Check that 'epoch' variable exists, convert it to tt2000 and filter data
    # between start_time/end_time if required
    try:
        epoch = data["epoch"][:].astype(float)
    except KeyError:
        logger.error('No valid "epoch" variable found in the input data')
        raise
    else:
        # Instantiate roc.rpl.time.Time class
        time_instance = Time()

        # Get start_time in TT2000
        if start_time:
            # Convert start_time into TT2000
            start_time_tt2000 = float(time_instance.utc_to_tt2000(start_time))
        else:
            # By default, get lowest possible value for TT2000 datatype
            start_time_tt2000 = -(2**64)

        # Get end_time in TT2000
        if end_time:
            # Convert end_time into TT2000
            end_time_tt2000 = float(time_instance.utc_to_tt2000(end_time))
        else:
            # By default, get highest possible value for TT2000 datatype
            end_time_tt2000 = 2**64

        # Define array indices to keep between start_time/end_time
        idx = (epoch >= start_time_tt2000) & (epoch <= end_time_tt2000)

        # Get record index values between start_time and end_time
        if any(idx):
            epoch = epoch[idx]
            nrec = epoch.shape[0]
        else:
            # If no data found in time range, exit method now
            return start_time, end_time, 0

        # Fill Epoch CDF zVariable
        epoch_min = epoch.min()
        epoch_max = epoch.max()
        cdf["Epoch"] = epoch
        cdf["Epoch"].attrs["SCALEMIN"] = time_instance.tt2000_to_utc(
            epoch_min, to_datetime=True
        )
        cdf["Epoch"].attrs["SCALEMAX"] = time_instance.tt2000_to_utc(
            epoch_max, to_datetime=True
        )

    # Fill other CDF zVariables
    for i, name in enumerate(data.dtype.names):
        # skip if epoch (already processed above)
        if name.lower() == "epoch":
            continue
        else:
            logger.debug(f"Writing {nrec} records for {name} zVariable...")

        if name.lower() == "quality_bitmask":
            # Make sure quality_bitmask is a UINT16
            data_i = data[name][idx].astype(np.uint16)
        else:
            data_i = data[name][idx]

        # Write data into the zVariable
        cdf[name.upper()] = data_i

        # Get min/max value of the current zVariable
        cdf[name.upper()].attrs["SCALEMIN"] = data_i.min()
        cdf[name.upper()].attrs["SCALEMAX"] = data_i.max()

    # Set quality_flag
    logger.debug('Set "QUALITY_FLAG" zVar default value to 3')
    cdf["QUALITY_FLAG"] = np.full(nrec, 3, dtype=np.uint8)
    cdf["QUALITY_FLAG"].attrs["SCALEMIN"] = 0
    cdf["QUALITY_FLAG"].attrs["SCALEMAX"] = 5

    return epoch_min, epoch_max, nrec


def l0_to_trange_cdf(
    task: type[Task],
    task_name: str,
    l0_file_list: list,
    output_dir: str,
    time_instance: Time = None,
    start_time: datetime = None,
    end_time: datetime = None,
    failed_files: list = None,
    processed_files: list = None,
    monthly: bool = False,
    unique: bool = False,
    overwrite: bool = False,
    is_cdag: bool = True,
):
    """
    Task to generate time range CDF from l0 file(s)

    :param task: instance of the task:
    :type task: Poppy Task class type object
    :param task_name: string containing the name of the task (as defined in descriptor)
    :type task_name: str
    :param l0_file_list: Input L0 files
    :type l0_file_list: list
    :param output_dir: path of the output directory
    :type output_dir: str
    :param time_instance: roc.rpl.time.Time object:
    :type time_instance: roc.rpl.time.Time
    :param start_time: start time of the data written in the output CDF
    :type start_time: datetime
    :param end_time: end time of the data written in the output CDF
    :type end_time: datetime
    :param failed_files: CDF files for which saving data has failed
    :type failed_files: list
    :param processed_files: CDF files for which saving data has succeeded
    :type processed_files: list
    :param monthly: Produce monthly file (Datetime format will be YYYYMMDD1-YYYYMMDD2,
                    where YYYYMMDD1 is the first day of the month and YYYYMMDD2 is the last day).
                    Month number is extracted from start_time value.
    :type monthly: bool
    :param unique: If True, make sure that return data are uniquely stored
    :type unique: bool
    :param overwrite: If True, overwrite existing output files
    :type overwrite: bool
    :param is_cdag: If True, generate 'CDAG' output files (CDAG == private data files)
    :type is_cdag: bool
    :return: output CDF filepath if it has been successfully generated, None otherwise
    :rtype: str
    """

    if not processed_files:
        processed_files = []
    if not failed_files:
        failed_files = []

    # Initialize output list (containing filepath)
    output_file_list = []

    # Create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # if True, add '-cdag' suffix to the end of the descriptor field in
    # the output filename
    # (used to indicate preliminary files to distributed to the CDAG members only)
    if is_cdag:
        logger.info(f'Producing "cdag" output CDF    [{task.job_id}]')

    # Retrieve list of output datasets to produce for the given task
    try:
        dataset_list = get_datasets(task, task_name)
    except Exception:
        raise LoadDataSetError(
            f"Cannot load the list of datasets to produce for {task_name}    [{task.job_id}]"
        )
    else:
        logger.debug(
            "Produce L1 CDF file(s) for the following dataset(s):"
            f" {[ds['name'] for ds in dataset_list]}    [{task.job_id}]"
        )

    # Get list of input l0 file(s)
    if not isinstance(l0_file_list, list):
        l0_file_list = [l0_file_list]

    # Sort input files
    l0_file_list = sorted(l0_file_list)
    # get number of files
    l0_file_len = len(l0_file_list)

    # Get L0 files time_min/time_max
    try:
        l0_time_min, l0_time_max = get_l0_trange(l0_file_list)
        if None in l0_time_min or None in l0_time_max:
            raise ValueError
    except TypeError:
        logger.error(f'Input "l0_files" must be a list!\t[{task.job_id}]')
        return []
    except ValueError:
        logger.error(f"Output L0 time min. or max. list is not valid!\t[{task.job_id}]")
        return []

    # Get start_time for output CDF (use time min of L0 files if not defined)
    if not start_time:
        start_time = task.pipeline.get("start_time", default=[min(l0_time_min)])[0]

    logger.debug(f"start_time value is {start_time}\t[{task.job_id}]")

    # Get end_time for output CDF (use time max of L0 files if not defined)
    if not end_time:
        end_time = task.pipeline.get("end_time", default=[max(l0_time_max)])[0]

    logger.debug(f"end_time value is {end_time}\t[{task.job_id}]")

    # Loops over each output dataset to produce for the current task
    for current_dataset in dataset_list:
        dataset_name = current_dataset["name"]
        data_descr = current_dataset["descr"]
        data_version = current_dataset["version"]

        logger.debug(
            "Running file production for the dataset "
            f"{dataset_name} (V{data_version})\t[{task.job_id}]"
        )

        # get the path to the master CDF file of this dataset
        master_cdf_dir = get_master_cdf_dir(task)

        # Get master cdf filename from descriptor
        master_cdf_file = data_descr["template"]

        # Build master file pattern
        master_pattern = os.path.join(master_cdf_dir, master_cdf_file)

        # Get master file path
        master_path = glob(master_pattern)

        # Check existence
        if not master_path:
            raise FileNotFoundError(
                "{0} master CDF not found for the dataset {1}!\t[{2}]".format(
                    master_pattern, dataset_name, task.job_id
                )
            )
        else:
            master_path = sorted(master_path)[-1]
            logger.info(
                'Producing dataset "{0}" with the master CDF "{1}"\t[{2}]'.format(
                    dataset_name, master_path, task.job_id
                )
            )

        # Initialize loop variables
        data = np.empty(0)
        parents = []
        # Loop over l0_files list
        for i, l0_file in enumerate(l0_file_list):
            with h5py.File(l0_file, "r") as l0:
                # Skip L0 file for which start_time/end_time is not inside the
                # time range
                if l0_time_max[i] < start_time or l0_time_min[i] > end_time:
                    logger.debug(
                        f"{l0_file} is outside the time range: "
                        f"[{start_time}, {end_time}], skip it\t[{task.job_id}]"
                    )
                    continue
                else:
                    logger.debug(
                        f"Processing {l0_file} [{l0_file_len - i - 1}]\t[{task.job_id}]"
                    )

                # Append current l0 file to parent list
                parents.append(os.path.basename(str(l0_file)))

                # Get TM packet(s) required to generate HK CDF for the current
                # dataset
                expected_packet = data_descr["packet"]
                # Check that TM packet(s) are in the input l0 data
                if not is_packet(expected_packet, l0["TM"]) and not is_packet(
                    expected_packet, l0["TC"]
                ):
                    logger.info(
                        f"No expected packet found for {dataset_name}"
                        f" in {l0_file} [{','.join(expected_packet)}]\t[{task.job_id}]"
                    )
                    continue

                # Get function to process data
                # IMPORTANT: function alias in import should have the same name
                # as the dataset alias in the descriptor
                func = dataset_func.get(dataset_name)
                if func is None:
                    logger.error(
                        f"No function found for {dataset_name}\t[{task.job_id}]"
                    )
                    failed_files.append(l0_file)
                    break

                # call the dataset-related function
                try:
                    logger.debug(f"Running {func}\t[{task.job_id}]")
                    result = func(l0, task)
                except Exception as e:
                    # TODO catch exception in the ROC database
                    logger.exception(
                        f'Running "{func}" function has failed\t[{task.job_id}]: \n{e}'
                    )
                    # TODO - Add the current failed dataset processing to failed_files
                    failed_files.append(l0_file)
                    continue

                # Make sure result is a numpy array and not a NoneType
                if result is None or result.shape[0] == 0:
                    logger.debug(
                        f"Returned {dataset_name} dataset array"
                        f" is empty for {l0_file}\t[{task.job_id}]"
                    )
                else:
                    logger.debug(
                        f"{result.shape[0]} {dataset_name} dataset samples"
                        f" returned from {l0_file}\t[{task.job_id}]"
                    )

                    # If data is empty
                    if data.shape[0] == 0:
                        # then store result
                        data = result
                    else:
                        # Else append new result into data
                        data = np.append(data, result, axis=0)

        # Checking resulting data length
        nrec = data.shape[0]
        if nrec == 0:
            logger.warning(
                "No data for dataset"
                f" {dataset_name}: skip output cdf creation\t[{task.job_id}]"
            )
            continue

        # reorder the data by increasing time
        data = order_by_increasing_time(data, unique=unique)

        # Generation date
        generation_date = datetime.now().strftime(INPUT_DATETIME_STRFTIME)
        logger.debug(
            f'Set "Generation_date" attr. value to {generation_date}\t[{task.job_id}]'
        )

        # file ID
        file_id = str(uuid.uuid4())
        logger.debug(f'Set "File_ID" attr. value to {file_id}\t[{task.job_id}]')

        # Re-define datetime and parents g.attribute for time range CDF data
        # products
        if monthly:
            # Get number of days in the start_time month
            mday_num = calendar.monthrange(start_time.year, start_time.month)[1]
            # Get latest day of the month
            mday_end = datetime(start_time.year, start_time.month, 1) + timedelta(
                days=mday_num - 1
            )
            # Build datetime metadata used to generate time ranged file name
            l0_datetime = "-".join(
                [
                    start_time.strftime(TIME_DAILY_STRFORMAT),
                    mday_end.strftime(TIME_DAILY_STRFORMAT),
                ]
            )
        else:
            l0_datetime = "-".join(
                [
                    start_time.strftime(CDF_TRANGE_STRFORMAT),
                    end_time.strftime(CDF_TRANGE_STRFORMAT),
                ]
            )
        l0_parents = [f"HDF5>{Path(parent).stem}" for parent in parents]

        # Set CDF global attributes using first l0_file metadata in the list
        with h5py.File(l0_file_list[0], "r") as l0:
            metadata = init_cdf_global(
                l0.attrs,
                task,
                master_path,
                overwrite={
                    "Datetime": l0_datetime,
                    "Parents": l0_parents,
                    "File_ID": file_id,
                    "Generation_date": generation_date,
                    "Data_version": data_version,
                    "MODS": data_descr["mods"],
                },
            )

        # Generate output CDF filename and open it
        filepath = generate_filepath(
            task, metadata, "cdf", is_cdag=is_cdag, overwrite=overwrite
        )

        # Get the instance of the output target
        target = task.outputs[dataset_name]

        # Add SPICE SCLK kernel as an entry
        # of the "Kernels" g. attr
        sclk_file = get_spice_kernels(
            time_instance=time_instance, pattern="solo_ANC_soc-sclk"
        )
        if sclk_file:
            metadata["SPICE_KERNELS"] = sclk_file[-1]
        else:
            logger.warning(
                f"No SPICE SCLK kernel saved for {filepath}\t[{task.job_id}]"
            )

        # open the target to update its status according to errors etc
        with target.activate():
            # create the file for the CDF containing results
            with CDF(filepath, master_path) as cdf:
                try:
                    # write zVariable data and associated variable attributes in
                    # the CDF
                    time_min, time_max, nrec = put_cdf_zvars(
                        cdf, data, start_time=start_time, end_time=end_time
                    )
                    if nrec > 0:
                        # Update TIME_MIN, TIME_MAX (in julian days)
                        metadata["TIME_MIN"] = (
                            str(time_instance.tt2000_to_utc(time_min)) + "Z"
                        ).replace(" ", "T")
                        metadata["TIME_MAX"] = (
                            str(time_instance.tt2000_to_utc(time_max)) + "Z"
                        ).replace(" ", "T")

                        # write global attribute entries on the CDF
                        put_cdf_global(cdf, metadata)
                    else:
                        logger.warning(
                            f"No data found between {start_time} and {end_time}"
                            f" to be written into {filepath}\t[{task.job_id}]"
                        )

                except Exception as e:
                    logger.exception(
                        f"{filepath} production has failed\t[{task.job_id}]:\n{e}"
                    )
                    cdf.attrs["Validate"] = "-1"
                    failed_files.append(filepath)

            if nrec == 0:
                logger.info(f"Removing empty file {filepath}...\t[{task.job_id}]")
                os.remove(filepath)
                filepath = ""
            elif os.path.isfile(filepath):
                processed_files.append(filepath)
                logger.info(f"{filepath} saved\t[{task.job_id}]")
                output_file_list.append(filepath)
            else:
                failed_files.append(filepath)
                logger.error(f"Writing {filepath} has failed!\t[{task.job_id}]")

            # Set output target filepath
            target.filepath = filepath

    return output_file_list


def get_l0_trange(l0_files: list, minmax: bool = False) -> tuple:
    """
    Get start_time/end_time from an input list of L0 files.

    :param l0_files: List of L0 files for which start_time/end_time must be extracted
    :type l0_files: list
    :param minmax: If True, return the minimal start_time value and maximal end_time value from over all the L0 files.
    :type minmax: bool
    :return: Input L0 files start_time/end_time (as datetime object)
    :rtype: tuple
    """

    if not isinstance(l0_files, list):
        raise TypeError

    # Get number of l0_files
    nl0 = len(l0_files)

    # Initialize start_time/end_time lists
    start_time = [None] * nl0
    end_time = [None] * nl0
    for i, l0_file in enumerate(l0_files):
        try:
            with h5py.File(l0_file, "r") as l0:
                # Get TIME_MIN/TIME_MAX L0 attributes value as datetime
                start_time[i] = datetime.strptime(
                    l0.attrs["TIME_MIN"], TIME_ISO_STRFORMAT
                )
                end_time[i] = datetime.strptime(
                    l0.attrs["TIME_MAX"], TIME_ISO_STRFORMAT
                )
        except Exception as e:
            logger.exception(f"Cannot parse {l0_file}: \n{e}")

    if minmax:
        return min(start_time), max(end_time)
    else:
        return start_time, end_time
