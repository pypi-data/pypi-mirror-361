#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tools for FILM plugin."""

import json
import os
import shutil
import argparse
from datetime import datetime
import glob
from typing import List, Union
from pathlib import Path

import numpy as np

from poppy.core import MissingProperty
from poppy.core.generic.metaclasses import Singleton
from poppy.core.configuration import Configuration
from poppy.core.generic.paths import Paths
from poppy.core.logger import logger
from roc.film.constants import (
    _ROOT_DIRECTORY,
    INPUT_DATETIME_STRFTIME,
    DATA_VERSION,
    TIME_DAILY_STRFORMAT,
)

from roc.film.exceptions import FilmException, HandlingFileError

__all__ = [
    "paths",
    "DESCRIPTOR",
    "raise_error",
    "valid_time",
    "valid_date",
    "valid_data_version",
    "valid_single_file",
    "valid_dir",
    "extract_datetime",
    "extract_file_fields",
    "get_datasets",
    "sort_indices",
    "unique_dict_list",
    "sort_dict_list",
    "safe_move",
    "setup_lock",
    "get_latest_file",
    "Map",
    "glob_list",
    "move_to_trash",
    "decode",
]

# ________________ Global Variables _____________
# (define here the global variables)

# create a path object that can be used to get some common path in the module
paths = Paths(_ROOT_DIRECTORY)

# ________________ Class Definition __________
# (If required, define here classes)

# ________________ Global Functions __________
# (If required, define here global functions)


def get_descriptor():
    """
    Read the content of the plugin descriptor

    :return: An instance of Descriptor containing the descriptor.json content
    """

    class Descriptor(object, metaclass=Singleton):
        def __init__(self):
            descriptor = paths.from_root("descriptor.json")

            # Get descriptor content
            with open(descriptor, "r") as file_buffer:
                for key, val in json.load(file_buffer).items():
                    setattr(self, key, val)

            # Re-organize task section
            tasks = dict()
            for task in self.tasks:
                tasks[task["name"]] = task

            self.tasks = tasks

    # read plugin descriptor
    return Descriptor()


DESCRIPTOR = get_descriptor()


def raise_error(message, exception=FilmException):
    """Add an error entry to the logger and raise an exception."""
    logger.error(message)
    raise exception(message)


def valid_time(t: str, str_format: str = INPUT_DATETIME_STRFTIME) -> datetime:
    """
    Validate input datetime string format.

    :param t: input datetime string
    :param str_format: expected datetime string format
    :return: datetime object with input datetime info
    """
    if t:
        try:
            return datetime.strptime(t, str_format)
        except ValueError:
            raise_error(
                f"Not a valid datetime: '{t}'.", exception=argparse.ArgumentTypeError
            )


def valid_date(t: str, str_format: str = TIME_DAILY_STRFORMAT) -> datetime:
    """
    Validate input date string format.

    :param t: input datetime string
    :param str_format: expected datetime string format
    :return: datetime object with input datetime info
    """
    if t:
        try:
            return datetime.strptime(t, str_format)
        except ValueError:
            raise_error(
                f"Not a valid date: '{t}'.", exception=argparse.ArgumentTypeError
            )


def valid_data_version(data_version: Union[str, int]) -> str:
    """
    Make sure to have a valid data version.

    :param data_version: integer or string containing the data version
    :return: string containing valid data version (i.e., 2 digits string)
    """
    try:
        if isinstance(data_version, list):
            data_version = data_version[0]
        data_version = int(data_version)
        return f"{data_version:02d}"
    except ValueError:
        raise_error(f"Input value for --data-version is not valid! ({data_version})")


def valid_single_file(file_to_validate: Union[str, list]) -> Union[str, Path]:
    """
    Make sure to have a valid single file.

    :param file_to_validate: 1-element list or string containing the path to the file
    :return: Path of the input file if it is valid
    """
    try:
        if isinstance(file_to_validate, list):
            file_to_validate = file_to_validate[0]
        if os.path.isfile(str(file_to_validate)):
            return file_to_validate
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        raise_error(
            f"Input file not found! ({file_to_validate})", exception=FileNotFoundError
        )
    except ValueError:
        raise_error(
            f"Input file is not valid! ({file_to_validate})", exception=ValueError
        )
    except Exception as e:
        raise_error(f"Problem with input file! ({file_to_validate})", exception=e)


def valid_dir(dir_to_validate: Union[str, Path]) -> Union[str, Path]:
    """
    Make sure to have a valid input directory.

    :param dir_to_validate: 1-element list or string containing the path to the directory
    :return:Path of the input directory if it is valid
    """
    try:
        if isinstance(dir_to_validate, list):
            dir_to_validate = dir_to_validate[0]
        if os.path.isdir(dir_to_validate):
            return dir_to_validate
        else:
            raise IsADirectoryError
    except IsADirectoryError:
        raise_error(
            f"Input directory not found! ({dir_to_validate})",
            exception=IsADirectoryError,
        )
    except ValueError:
        raise_error(
            f"Input directory is not valid! ({dir_to_validate})", exception=ValueError
        )
    except Exception as e:
        raise_error(f"Problem with input directory! ({dir_to_validate})", exception=e)


def unique_dates(utc_times: list) -> List[datetime.date]:
    """
    Get list of unique dates from input list of utc_time

    :param utc_times: list of packet utc_time (datetime)
    :return: list of unique dates (datetime.date())
    """

    dates = list()
    for utc_time in utc_times:
        date = utc_time.date()
        if date not in dates:
            dates.append(date)

    return dates


def extract_datetime(str_datetime: str, str_tformat: str = "%Y%m%d") -> List[datetime]:
    """
    Extract Datetime attribute value.

    :param str_datetime: String containing Datetime attribute value (can be time range or daily format)
    :param str_tformat: expected datetime string format
    :return: Datetime start/end times. If input Datetime has a daily format, return 1-element list.
    """
    out_datetime = None

    str_datetime_list = str_datetime.split("-")

    if len(str_datetime_list) == 1:
        out_datetime = [datetime.strptime(str_datetime, str_tformat)]
    elif len(str_datetime_list) == 2:
        out_datetime = [datetime.strptime(dt, str_tformat) for dt in str_datetime_list]
    else:
        logger.error(f"Wrong file name format: {str_datetime}")

    return out_datetime


def get_latest_file(file_list: list) -> Union[Path, str]:
    """
    Get the latest version file from an input list of files.
    Input files must be formatted using ROC standards
    and must be from the same dataset (i.e., only date and/or version must differ).

    :param file_list: List of input files
    :return: path to the latest file
    """

    # Ordering input file list by alphabetical/numerical characters
    file_list.sort(key=lambda x: os.path.basename(x))

    return file_list[-1]


def get_datasets(task, task_name):
    """
    Retrieve list of output datasets and related description from the descriptor for a given task

    :param task: Instance of the task
    :param task_name: Name of the task
    :return: list of output datasets to produce
    """

    # Get dataset JSON file provided as an input argument (if any)
    dataset_file = task.pipeline.get("dataset_file", default=[None], args=True)[0]
    # Get --dataset input keyword value (if any)
    dataset_names = task.pipeline.get("dataset", default=[None], args=True)
    # Get --data-version input keyword value (if any)
    data_version = task.pipeline.get("data_version", default=[DATA_VERSION], args=True)[
        0
    ]

    # Get task output dataset description list from the descriptor.json file
    task_output_list = DESCRIPTOR.tasks[task_name]["outputs"]

    # If dataset JSON file passed as an value of the --dataset_file input
    # keyword, load list of datasets to create and related data_version
    # (optional)
    if dataset_file and os.path.isfile(dataset_file):
        with open(dataset_file, "r") as file_buff:
            # Loop over dataset array in the JSON file to get the name and
            # optionally the version of the output file
            dataset_to_create = []
            data_versions = []
            for current_dataset_obj in json.load(file_buff)["dataset"]:
                dataset_to_create.append(current_dataset_obj["name"])
                data_versions.append(current_dataset_obj.get("version", data_version))
    elif dataset_names[0]:
        # Else if dataset list passed as values of the --dataset input keyword
        dataset_to_create = dataset_names
        data_versions = [data_version] * len(dataset_to_create)
    else:
        # Else load all the output datasets listed in descriptor for the given
        # task by default
        dataset_to_create = list(DESCRIPTOR.tasks[task_name]["outputs"].keys())
        data_versions = [data_version] * len(dataset_to_create)

    # Retrieve dataset info from descriptor.json
    dataset_list = []
    for i, dataset_name in enumerate(dataset_to_create):
        # Check if current dataset is indeed a output dataset of the task (as
        # described in the descriptor.json file)
        if dataset_name not in task_output_list:
            logger.warning(
                f"{dataset_name} is not a valid dataset of the task {task_name}!"
            )
        else:
            # if yes, get description and store info in the dataset_list list
            current_dataset = {
                "name": dataset_name,
                "version": data_versions[i],
                "descr": task_output_list[dataset_name],
            }
            dataset_list.append(current_dataset)

    return dataset_list


def unique_dict_list(list_of_dict: List[dict]) -> List[dict]:
    """
    Unify an input list of dict.

    :param list_of_dict: List of dict to unify
    :return: return list inside which each dict is unique
    """
    return [i for n, i in enumerate(list_of_dict) if i not in list_of_dict[n + 1 :]]


def sort_dict_list(list_of_dict: List[dict], key: object) -> List[dict]:
    """
    Sort a list of dictionaries
    using a given keyword in the dictionaries.

    :param list_of_dict: List of dictionaries to sort
    :param key: keyword of dictionaries used for sorting
    :return: sorted list of dict.
    """
    return sorted(list_of_dict, key=lambda i: i[key])


def sort_indices(list_to_sort: list) -> list:
    """
    Return sorted indices of an input list

    :param list_to_sort: list for which sorted indices must be returned
    :return: list of sorted indices
    """

    return sorted(range(len(list_to_sort)), key=lambda k: list_to_sort[k])


def safe_move(src: str, dst: str, ignore_patterns: Union[list, None] = None) -> bool:
    """
    Perform a safe move of a file or directory.

    :param src: string containing the path of the file/directory to move
    :param dst: string containing the path of the target file/directory
    :param ignore_patterns: string containing the file patterns to ignore (for copytree only)
    :return: True if the move has succeeded, False otherwise
    """
    if not ignore_patterns:
        ignore_patterns = []

    # Initialize output
    is_copied = False

    # First do a copy...
    try:
        if os.path.isfile(src):
            shutil.copy(src, dst, follow_symlinks=True)
        elif os.path.isdir(src):
            shutil.copytree(
                src,
                dst,
                ignore=shutil.ignore_patterns(*ignore_patterns),
                dirs_exist_ok=True,
            )
    except Exception:
        raise HandlingFileError(f"Cannot move {src} into {dst}!")
    else:
        # then delete if the file has well copied
        if os.path.exists(dst):
            is_copied = True
            if os.path.isfile(src):
                os.remove(src)
            elif os.path.isdir(src):
                shutil.rmtree(src)

    return is_copied


def setup_lock(pipeline):
    """
    Set the Lock class filename and dirpath attributes
    from incoming lock_file argument (if any)

    :param pipeline: Poppy Pipeline instance
    :return:
    """

    # Retrieve lock_file input argument value
    lock_file = pipeline.get("lock_file", default=[None], args=True)[0]
    if lock_file is not None:
        # Retrieve output directory path
        from roc.film.tools.file_helpers import get_output_dir

        output_dir = get_output_dir(pipeline)

        # Set the value of Pipeline.lock attribute filename
        pipeline.lock_path = output_dir, os.path.basename(lock_file)


def sort_cdf_by_epoch(cdf, descending=False, zvar_list=[]):
    """
    Sort input CDF content by ascending Epoch time values

    :param cdf: input CDF to sort (pycdf.CDF object)
    :param descending: If True, sort by descending Epoch time values
    :param zvar_list: List of zvars to reorder. Default is all zvars in the CDF
    :return: Epoch time sorted CDF (pycdf.CDF object)
    """

    try:
        epoch = cdf["Epoch"]
    except Exception:
        logger.error("Cannot get Epoch zVariable from input CDF!")
        return cdf

    sorted_idx = np.argsort(epoch[...])
    if descending:
        sorted_idx = sorted_idx[::-1]

    if zvar_list is None:
        zvar_list = list(cdf.keys())

    for zvar in zvar_list:
        current_zvar = cdf[zvar][...]
        current_zvar = current_zvar[sorted_idx,]
        cdf[zvar] = current_zvar

    return cdf


def extract_file_fields(
    rpw_file: Union[Path, str],
) -> list:
    """
    Extract RPW file fields (assuming SolO file naming standards)

    :param rpw_file: RPW file to split
    :return: list of file fields
    """
    fields = Path(rpw_file).stem.split("_")

    if len(fields) < 5:
        logger.error(f'Cannot extract file fields: invalid input file "{rpw_file}"!')
        raise ValueError

    return fields


class Map(dict):
    """
    Use a dictionary as an object accessing attributes with dot
    See https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


def glob_list(list_of_files: list) -> list:
    """
    Apply glob.glob() method on a list of input files.
    It permits to expand possible regex in the list of files.

    :param list_of_files: List of input files (strings)
    :type:list
    :return: list of files globbed
    :rtype: list
    """
    output_list = []
    for current_file in list_of_files:
        output_list.extend(glob.glob(str(current_file)))
    return output_list


def move_to_trash(file_or_dir):
    """
    Moveh the input file or directory to the pipeline trash.

    :param file_or_dir: file or directory to move
    :return: If succeeded, the path of the file/dir in the trash. None otherwise
    """
    # Get trash directory
    trash_dir = get_trash_dir()

    if os.path.isfile(file_or_dir):
        is_file = True
    else:
        is_file = False

    try:
        logger.debug(f"Moving {file_or_dir} into {trash_dir}")
        target_path = os.path.join(trash_dir, os.path.basename(file_or_dir))
        shutil.copyfile(file_or_dir, target_path)
        if os.path.exists(target_path):
            # Remove source file (only if target file has been well copied)
            if is_file:
                os.remove(file_or_dir)
            else:
                shutil.rmtree(file_or_dir)
    except Exception:
        logger.exception(f"Moving {file_or_dir} into {trash_dir} has failed!")
        target_path = None

    return target_path


def get_trash_dir():
    """
    Return the path of the ROC pipeline trash folder.
    Raise an error if not defined

    :return: path of the ROC pipeline trash folder
    """

    # Get trash folder path
    if "ROC_PIP_TRASH_DIR" in Configuration.manager["pipeline"]["environment"]:
        trash_dir = Configuration.manager["pipeline"]["environment.ROC_PIP_TRASH_DIR"]
    elif "ROC_PIP_TRASH_DIR" in os.environ:
        trash_dir = os.environ["ROC_PIP_TRASH_DIR"]
    else:
        raise MissingProperty("ROC_PIP_TRASH_DIR variable is not defined!")

    return trash_dir


def decode(binary, encoding="UTF-8"):
    """
    Decode input binary into string.

    :param binary: binary/ies to decode
    :param encoding: See string.decode() encoding keyword
    :return: Decoded string(s)
    """
    if isinstance(binary, str):
        return binary
    elif isinstance(binary, list):
        return [element.decode(encoding) for element in binary]
    elif isinstance(binary, np.ndarray):

        def f(x):
            return x.decode(encoding)

        return np.vectorize(f)(binary)
    elif isinstance(binary, bytes):
        return binary.decode(encoding)
    else:
        raise ValueError(f"Input binary type ({type(binary)}) is not valid!")
