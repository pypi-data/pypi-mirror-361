##########################################################################
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
##########################################################################

"""
Module for caching arguments passed to batch jobs.

This module provides two backends for caching:
1. In-memory cache for local runs.
2. Persistent cache using the dt__Blob module for remote runs.

The cache stores arguments as a dictionary of dictionaries, where the outer dictionary's keys are job names
and the inner dictionaries contain the arguments.

This module is for internal use of the datatailr package.
"""

from collections import defaultdict
import pickle
from typing import Any, Dict

from datatailr import is_dt_installed, Blob
from datatailr.scheduler import BatchJob


__BLOB_STORAGE__ = Blob()


class ArgumentsCache:
    def __init__(self, use_persistent_cache: bool = is_dt_installed()):
        """
        Initialize the ArgumentsCache.

        :param use_persistent_cache: If True, use the persistent cache backend. Otherwise, use in-memory cache.
        """
        self.use_persistent_cache = use_persistent_cache
        self.in_memory_cache: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(
            lambda: defaultdict(dict)
        )

    def add_arguments(self, batch_run_id: str, job: str, arguments: Dict[str, Any]):
        """
        Add arguments to the cache for a specific job and batch run.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :param arguments: Dictionary of arguments to store.
        """
        if self.use_persistent_cache and isinstance(job, str):
            path = f"{batch_run_id}/{job}/args"
            self._add_to_persistent_cache(path, arguments)
        else:
            self.in_memory_cache[batch_run_id][job]["args"] = arguments

    def get_arguments(self, batch_run_id: str, job: str) -> Dict[str, Any]:
        """
        Retrieve arguments from the cache for a specific job and batch run.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :return: Dictionary of arguments.
        """
        if self.use_persistent_cache and isinstance(job, str):
            path = f"{batch_run_id}/{job}/args"
            arg_keys = self._get_from_persistent_cache(path)
            if not isinstance(arg_keys, dict):
                raise TypeError(
                    f"Expected a dictionary for arguments, got {type(arg_keys)}"
                )
        else:
            arg_keys = (
                self.in_memory_cache.get(batch_run_id, {})
                .get(job, {})
                .get("args", {})
                .items()
            )
        arguments = {}
        for key, value in arg_keys:
            if isinstance(value, BatchJob):
                arguments[key] = value.name
            else:
                arguments[key] = value
        return arguments

    def add_result(self, batch_run_id: str, job: str, result: Any):
        """
        Add the result of a batch job to the cache.

        :param batch_run_id: Identifier for the batch run.
        :param job: Name of the job.
        :param result: Result of the batch job.
        """
        if self.use_persistent_cache and isinstance(job, str):
            path = f"{batch_run_id}/{job}/result"
            self._add_to_persistent_cache(path, result)
        else:
            self.in_memory_cache[batch_run_id][job]["result"] = result

    def get_result(self, batch_run_id: str, job: str) -> Any:
        """
        Retrieve the result of a batch job from the cache.

        :param batch_run_id: Identifier for the batch run.
        :param job: Name of the job.
        :return: Result of the batch job.
        """
        if self.use_persistent_cache and isinstance(job, str):
            path = f"{batch_run_id}/{job}/result"
            return self._get_from_persistent_cache(path)
        return self.in_memory_cache[batch_run_id][job].get("result")

    def _add_to_persistent_cache(self, path: str, blob: Any):
        """
        Add arguments to the persistent cache.
        This method serializes the blob using pickle and stores it in the Blob storage.
        :param path: Path in the Blob storage where the blob will be stored.
        :param blob: The blob to store, typically a dictionary of arguments.
        :raises TypeError: If the blob cannot be pickled.

        """
        __BLOB_STORAGE__.put_blob(
            path, pickle.dumps(blob, protocol=pickle.HIGHEST_PROTOCOL)
        )

    def _get_from_persistent_cache(self, path: str) -> Any:
        """
        Retrieve arguments from the persistent cache.

        :param path: Path in the Blob storage where the blob is stored.
        """
        try:
            data = __BLOB_STORAGE__.get_blob(path)
            return pickle.loads(data)
        except (TypeError, EOFError):
            return {}
