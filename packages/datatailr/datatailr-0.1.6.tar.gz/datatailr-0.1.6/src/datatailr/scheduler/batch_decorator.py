# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import functools
import inspect
import os

from datatailr.logging import DatatailrLogger
from datatailr.scheduler.arguments_cache import ArgumentsCache
from datatailr.scheduler.base import EntryPoint, JobType, Resources
from datatailr.scheduler.batch import BatchJob, get_current_manager
from datatailr.scheduler.constants import DEFAULT_TASK_CPU, DEFAULT_TASK_MEMORY
from datatailr.scheduler.utils import get_available_env_args

__ARGUMENTS_CACHE__ = ArgumentsCache()
__FUNCTIONS_CREATED_IN_DAG__: dict[BatchJob, str] = {}
logger = DatatailrLogger(__name__).get_logger()


def batch_run_id() -> str:
    return os.environ["DATATAILR_BATCH_RUN_ID"]


def dag_id(job: BatchJob) -> str:
    return os.getenv(
        "DATATAILR_BATCH_ID", __FUNCTIONS_CREATED_IN_DAG__.get(job, "unknown")
    )


def batch_decorator(memory=DEFAULT_TASK_MEMORY, cpu=DEFAULT_TASK_CPU):
    """
    Decorator to mark a function as a batch job.
    This decorator can be used to wrap functions that should be executed as part of batch jobs.
    """

    def decorator(func) -> BatchJob:
        spec = inspect.getfullargspec(func)
        signature = inspect.signature(func)
        varargs = spec.varargs
        varkw = spec.varkw
        parameters = signature.parameters

        @functools.wraps(func)
        def batch_main(*args, **kwargs):
            dag = get_current_manager()
            if dag is None:
                logger.info(f'Function "{func.__name__}" is being executed.')
                # There are two possible scenarios:
                # 1. The function is called directly, not as part of a batch job. In this case, the args and kwargs should be used.
                # 2. The function is called as part of a batch job - it was constructed as part of a DAG and is now being executed.
                if func not in __FUNCTIONS_CREATED_IN_DAG__:
                    return func(*args, **kwargs)
                function_arguments = [v.name for v in parameters.values()]
                env_args = get_available_env_args()
                final_args = list(args)
                final_kwargs = kwargs.copy()

                for name, value in env_args.items():
                    if name in function_arguments:
                        if len(final_args) < len(function_arguments):
                            final_args.extend(
                                [None] * (len(function_arguments) - len(final_args))
                            )
                        final_args[function_arguments.index(name)] = value
                function_arguments = __ARGUMENTS_CACHE__.get_arguments(
                    dag_id(func), func.__name__
                )
                result = func(**function_arguments)
                __ARGUMENTS_CACHE__.add_result(batch_run_id(), func.__name__, result)
                return result
            else:
                __FUNCTIONS_CREATED_IN_DAG__[func] = dag.id
                all_args = dict(zip(spec.args, args)) | kwargs

                __ARGUMENTS_CACHE__.add_arguments(dag.id, func.__name__, all_args)

                dag.set_autorun(True)
                job = BatchJob(
                    name=func.__name__,
                    entrypoint=EntryPoint(
                        JobType.BATCH,
                        module_name=func.__module__,
                        function_name=func.__name__,
                    ),
                    resources=Resources(memory=memory, cpu=cpu),
                    dependencies=[
                        value.name
                        for _, value in all_args.items()
                        if isinstance(value, BatchJob)
                    ],
                    dag=dag,
                )
                return job

        module = inspect.getmodule(func)
        if hasattr(module, "__batch_main__"):
            if func.__name__ in getattr(module, "__batch_main__"):
                raise ValueError(f"Duplicate batch main function {func.__name__}")
            module.__batch_main__[func.__name__] = batch_main  # type: ignore
        else:
            setattr(module, "__batch_main__", {func.__name__: batch_main})

        # The return type is a BatchJob, but we use type: ignore to avoid type checking issues
        return batch_main  # type: ignore

    return decorator
