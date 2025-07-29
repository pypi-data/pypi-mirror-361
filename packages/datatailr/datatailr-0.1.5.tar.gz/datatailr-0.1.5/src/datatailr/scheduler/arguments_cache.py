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
from typing import Any, Dict

from datatailr import is_dt_installed
from datatailr.scheduler import BatchJob


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
            self._add_to_persistent_cache(batch_run_id, job, arguments)
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
            return self._get_from_persistent_cache(batch_run_id, job)
        arguments = {}
        for key, value in (
            self.in_memory_cache.get(batch_run_id, {})
            .get(job, {})
            .get("args", {})
            .items()
        ):
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
            self._add_to_persistent_cache(batch_run_id, job, {"result": result})
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
            return self._get_from_persistent_cache(batch_run_id, job).get("result")
        return self.in_memory_cache[batch_run_id][job].get("result")

    def _add_to_persistent_cache(
        self, batch_run_id: str, job_name: str, arguments: Dict[str, Any]
    ):
        """
        Add arguments to the persistent cache.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :param arguments: Dictionary of arguments to store.
        """
        pass

    def _get_from_persistent_cache(
        self, batch_run_id: str, job_name: str
    ) -> Dict[str, Any]:
        """
        Retrieve arguments from the persistent cache.

        :param batch_run_id: Identifier for the batch run.
        :param job_name: Name of the job.
        :return: Dictionary of arguments.
        """
        return {}
