#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tasks for file handling in FILM plugin."""

import os
import shutil
import uuid
from pathlib import Path

from poppy.core.logger import logger
from poppy.core.task import Task

__all__ = ["MoveToProdDir", "MoveFailedFiles", "CopyFailedDds", "CopyProcessedDds"]

from roc.film.tools.tools import safe_move

from roc.film.tools.file_helpers import get_output_dir, get_products_dir


class MoveToProdDir(Task):
    """Task to move output files folder to
    final products directory."""

    plugin_name = "roc.film"
    name = "move_to_products_dir"

    def run(self):
        # TODO - add a lock file mechanism but at the task level
        #   (useful here to make sure that the
        #   a folder in the products_dir is not moved/removed while
        #   the pipeline is still working on it
        #   Add a LockFile class instance to the Task class in Poppy ?

        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.debug(f"Task {self.job_id} is starting")

        # See if --no-move keyword is defined
        no_move = self.pipeline.get("no_move", default=False, args=True)
        if no_move:
            logger.debug(
                f'--no-move is passed: skip current task "move_to_products_dir"\t[{self.job_id}]'
            )
            return

        # Retrieve pipeline output file directory
        output_dir = get_output_dir(self.pipeline)

        # Retrieve path of the product directory where output file directory
        # shall be moved
        products_dir = get_products_dir(self.pipeline)

        # Ignore possible items in the output directory
        ignore_patterns = []

        if not products_dir:
            logger.debug(
                f'products_dir argument not defined: Skip current task "move_to_products_dir"\t[{self.job_id}]'
            )
        else:
            output_dirbasename = os.path.basename(output_dir)
            target_dir = os.path.join(products_dir, output_dirbasename)
            logger.debug(f"Moving {output_dir} into {products_dir}")
            if safe_move(output_dir, target_dir, ignore_patterns=ignore_patterns):
                logger.info(f"{output_dir} moved into {products_dir}")
                # Finally remove any lock file from target_dir
                for current_lock in Path(target_dir).glob("*.lock"):
                    current_lock.unlink(missing_ok=True)
                    logger.debug(f"{current_lock} deleted")

        logger.debug(f"Task {self.job_id} completed")


class MoveFailedFiles(Task):
    """Move any failed files found
    into a 'failed' subdirectory."""

    plugin_name = "roc.film"
    name = "move_failed_files"

    def setup_inputs(self):
        # Retrieve list of failed files
        self.failed_file_list = self.pipeline.get("failed_files", default=[])
        self.failed_file_count = len(self.failed_file_list)

        # Retrieve output directory
        self.output_dir = get_output_dir(self.pipeline)

        # Retrieve failed_dir
        self.failed_dir = self.pipeline.get("failed_dir", default=[])

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.debug(f"Task {self.job_id} is starting")
        try:
            self.setup_inputs()
        except Exception:  # noqa
            logger.exception(f"Initializing inputs has failed for {self.job_id}!")
            self.pipeline.exit()
            return

        if self.failed_file_count == 0:
            logger.debug("No failed file(s) to move\t[{self.job_id}")
        else:
            # Loop over failed files list
            for i, failed_file in enumerate(self.failed_file_list):
                if not self.failed_dir:
                    failed_dir = os.path.join(os.path.dirname(failed_file), "failed")
                else:
                    failed_dir = self.failed_dir

                # Make failed subdir if not exists
                os.makedirs(failed_dir, exist_ok=True)

                # if failed item is a file
                if os.path.isfile(failed_file):
                    # Get failed file basename
                    failed_basename = os.path.basename(failed_file)

                    # target file path
                    target_filepath = os.path.join(failed_dir, failed_basename)

                    # perform a safe move (i.e., copy, check and delete) into
                    # failed dir
                    if safe_move(failed_file, target_filepath):
                        logger.warning(
                            f"{failed_file} moved into {failed_dir}\t[{self.job_id}]"
                        )

        logger.debug(f"Task {self.job_id} completed")


class CopyProcessedDds(Task):
    """
    Task to copy processed DDs files into a dedicated directory.
    """

    plugin_name = "roc.film"
    name = "copy_processed_dds"

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.debug(f"Task {self.job_id} is starting")

        # Get processed file target directory
        processed_dir = self.pipeline.get(
            "processed_dds_dir", default=[None], args=True
        )[0]

        # skip task if processed_dir is None
        if processed_dir is None:
            logger.info(
                f"No processed_dds_dir argument defined: skip task copy_processed_dds\t[{self.job_id}]"
            )
            return
        elif not os.path.isdir(processed_dir):
            logger.debug(f"Creating {processed_dir}...\t[{self.job_id}]")
            os.makedirs(processed_dir)
        else:
            logger.debug(f"process_dir set to {processed_dir}\t[{self.job_id}]")

        # If processed_files list not defined in the pipeline properties,
        # initialize it
        processed_file_list = self.pipeline.get("processed_dds_files", default=[])
        processed_files_count = len(processed_file_list)
        # Skip task if no processed files
        if processed_files_count == 0:
            logger.info(
                f"No processed file to move: skip task copy_processed_dds\t[{self.job_id}]"
            )
            return

        # Get clear-dds keyword
        clear_dds = self.pipeline.get("clear_dds", default=False)

        # Get list of failed files too
        failed_file_list = self.pipeline.get("failed_dds_files", default=[])

        # Loop over processed files to copy
        for processed_file in processed_file_list.copy():
            # Check first that processed file is not in failed list
            if processed_file in failed_file_list:
                logger.warning(
                    f"{processed_file} found in the failed file list!\t[{self.job_id}]"
                )
                continue

            # Build target filepath
            basename = os.path.basename(processed_file)
            target_filepath = os.path.join(processed_dir, basename)

            # copy file
            logger.debug(
                f"Copying {processed_file} into {processed_dir}\t[{self.job_id}]"
            )
            try:
                shutil.copyfile(processed_file, target_filepath)
            except Exception as e:
                logger.exception(
                    f"Copying {processed_file} into {processed_dir} has failed!\t[{self.job_id}]"
                )
                logger.debug(e)
            else:
                logger.info(
                    f"{processed_file} copied into {target_filepath}\t[{self.job_id}]"
                )

            # Remove current file from the list in pipeline properties
            processed_file_list.remove(processed_file)

            # if clear-dds keyword is passed, then remove processed Dds
            if clear_dds:
                os.remove(processed_file)
                logger.debug(f"{processed_file} deleted\t[{self.job_id}]")


class CopyFailedDds(Task):
    """
    Task to copy failed DDs files into a dedicated directory.
    """

    plugin_name = "roc.film"
    name = "copy_failed_dds"

    def run(self):
        # Define task job ID (long and short)
        self.job_uuid = str(uuid.uuid4())
        self.job_id = self.job_uuid[:8]
        logger.debug(f"Task {self.job_id} is starting")

        # Get failed file target directory
        failed_dir = self.pipeline.get("failed_dds_dir", default=[None], args=True)[0]
        # skip task if failed_dir is None
        if failed_dir is None:
            logger.info(
                f"No failed_dds_dir argument defined: skip task copy_failed_dds\t[{self.job_id}]"
            )
            return
        elif not os.path.isdir(failed_dir):
            logger.debug(f"Creating {failed_dir}...\t[{self.job_id}]")
            os.makedirs(failed_dir)
        else:
            logger.debug(f"failed_dir set to {failed_dir}\t[{self.job_id}]")

        # If failed_files list not defined in the pipeline properties,
        # initialize it
        failed_file_list = self.pipeline.get("failed_dds_files", default=[])
        failed_files_count = len(failed_file_list)
        # Skip task if no failed dds files
        if failed_files_count == 0:
            logger.info(
                f"No failed file to move: skip task copy_failed_dds\t[{self.job_id}]"
            )
            return

        # Get clear-dds keyword
        clear_dds = self.pipeline.get("clear_dds", default=False)

        # Loop over failed files to copy
        for failed_file in failed_file_list.copy():
            # Build target filepath
            basename = os.path.basename(failed_file)
            target_filepath = os.path.join(failed_dir, basename)

            # copy file
            logger.debug(f"Copying {failed_file} into {failed_dir}\t[{self.job_id}]")
            try:
                shutil.copyfile(failed_file, target_filepath)
            except Exception as e:
                logger.exception(
                    f"Copying {failed_file} into {failed_dir} has failed!\t[{self.job_id}]"
                )
                logger.debug(e)
            else:
                logger.info(
                    f"{failed_file} copied into {target_filepath}\t[{self.job_id}]"
                )

            # Remove current file from the list in pipeline properties
            failed_file_list.remove(failed_file)

            # if clear-dds keyword is passed, then remove processed Dds
            if clear_dds:
                os.remove(failed_file)
                logger.debug(f"{failed_file} deleted\t[{self.job_id}]")

        # Get failed tmraw list
        failed_tmraw_list = self.pipeline.get("failed_tmraw", default=[])
        failed_tmraw_count = len(failed_tmraw_list)
        # Skip task if no failed tmraw
        if failed_tmraw_count == 0:
            logger.debug("No failed tmraw to write\t[{self.job_id}]")
            return
        else:
            # Else save list of failed tmraw into text file
            tmraw_failed_file = os.path.join(failed_dir, "tmraw_failed.log")
            with open(tmraw_failed_file, "a") as fw:
                fw.writelines(failed_tmraw_list)
            logger.info(
                f"{failed_tmraw_count} failed TmRaw entries "
                f"saved into {tmraw_failed_file}\t[{self.job_id}]"
            )
