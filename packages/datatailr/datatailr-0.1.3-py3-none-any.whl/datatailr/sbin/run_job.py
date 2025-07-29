#!/usr/bin/env python3

# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import importlib
import os
import pickle

from datatailr import dt__Blob
from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


def main():
    entry_point = os.environ.get("DATATAILR_BATCH_ENTRYPOINT")
    batch_run_id = os.environ.get("DATATAILR_BATCH_RUN_ID")
    batch_id = os.environ.get("DATATAILR_BATCH_ID")
    job_id = os.environ.get("DATATAILR_JOB_ID")

    if entry_point is None:
        raise ValueError(
            "Environment variable 'DATATAILR_BATCH_ENTRYPOINT' is not set."
        )
    if batch_run_id is None:
        raise ValueError("Environment variable 'DATATAILR_BATCH_RUN_ID' is not set.")
    if batch_id is None:
        raise ValueError("Environment variable 'DATATAILR_BATCH_ID' is not set.")
    if job_id is None:
        raise ValueError("Environment variable 'DATATAILR_JOB_ID' is not set.")

    module_name, func_name = entry_point.split(":", 1)
    module = importlib.import_module(module_name)
    function = getattr(module, func_name)
    if not callable(function):
        raise ValueError(
            f"The function '{func_name}' in module '{module_name}' is not callable."
        )
    result = function()
    result_path = f"batch-results-{batch_run_id}-{job_id}.pkl"
    with open(result_path, "wb") as f:
        pickle.dump(result, f)
    blob = dt__Blob()
    blob.cp(result_path, "blob://")
    logger.info(f"{result_path} copied to blob storage.")


if __name__ == "__main__":
    try:
        logger.debug("Starting job execution...")
        main()
        logger.debug("Job executed successfully.")
    except Exception as e:
        logger.error(f"Error during job execution: {e}")
        raise
