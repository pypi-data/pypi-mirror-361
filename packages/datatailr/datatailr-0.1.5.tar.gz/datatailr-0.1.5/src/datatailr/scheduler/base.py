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
import json
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Tuple, Union

from datatailr import ACL, Environment, User, dt__Job, is_dt_installed
from datatailr.build.image import Image
from datatailr.errors import BatchJobError
from datatailr.logging import DatatailrLogger

logger = DatatailrLogger(os.path.abspath(__file__)).get_logger()


class RepoValidationError(BatchJobError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class JobType(Enum):
    """
    Enum representing different types of DataTailr jobs.
    """

    BATCH = "batch"
    SERVICE = "service"
    APP = "app"
    UNKNOWN = "unknown"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"JobType.{self.name}('{self.value}')"


@dataclass
class Resources:
    """
    Represents the resources required for a job.
    """

    memory: str = "100m"
    cpu: int = 1


class EntryPoint:
    """
    Represents an entry point for a DataTailr job.
    This can be a function or a callable object.
    """

    def __init__(
        self,
        type: JobType,
        func: Optional[Callable] = None,
        module_name: Optional[str] = None,
        function_name: Optional[str] = None,
    ):
        if func is None and (module_name is None or function_name is None):
            raise ValueError(
                "Either a function or module and function names must be provided."
            )
        self.func = func
        self.module_name = func.__module__ if func else module_name
        self.function_name = func.__name__ if func else function_name
        self.type = type

    def __call__(self, *args, **kwargs):
        if self.type == JobType.BATCH:
            if self.module_name and self.function_name:
                module = importlib.import_module(self.module_name)
                func = getattr(module, self.function_name)
            elif self.func is not None:
                func = self.func
            return func(*args, **kwargs)

        elif self.type == JobType.SERVICE:
            raise NotImplementedError("Service jobs are not yet implemented.")

        elif self.type == JobType.APP:
            raise NotImplementedError("App jobs are not yet implemented.")

    def __repr__(self):
        return f"EntryPoint({self.function_name} from {self.module_name}, type={self.type})"

    def __str__(self):
        return f"{self.module_name}.{self.function_name}"


class Job:
    def __init__(
        self,
        environment: Optional[Environment],
        name: str,
        image: Image,
        run_as: Optional[Union[str, User]],
        resources: Resources = Resources(memory="100m", cpu=1),
        acl: Optional[ACL] = None,
    ):
        if run_as is None:
            run_as = User.signed_user()
        if environment is None:
            environment = Environment.DEV
        elif isinstance(environment, str):
            environment = Environment(environment.lower())
        if isinstance(environment, str):
            environment = Environment(environment)
        self.acl = acl or ACL(user=run_as)
        self.environment = environment
        self.name = name
        self.run_as = run_as
        self.resources = resources
        self.image = image

        # Placeholders, to be set in derived classes
        self.type: JobType = JobType.UNKNOWN
        self.entrypoint = None
        self.__id = str(uuid.uuid4())

    @property
    def id(self) -> str:
        """
        Unique identifier for the job.
        """
        return self.__id

    def __repr__(self):
        return (
            f"Job(name={self.name}, environment={self.environment}, "
            f"run_as={self.run_as}, resources={self.resources}, "
            f"acl={self.acl}, type={self.type}, "
            f"entrypoint={self.entrypoint}, image={self.image})"
        )

    def to_dict(self):
        """
        Convert the Job instance to a dictionary representation.
        """
        job_dict = {
            "environment": str(self.environment),
            "image": self.image.to_dict(),
            "type": str(self.type) if self.type else None,
            "name": self.name,
            "run_as": self.run_as.name
            if isinstance(self.run_as, User)
            else self.run_as,
            "acl": self.acl.to_dict(),
        }
        if self.type != JobType.BATCH:
            job_dict["entrypoint"] = str(self.entrypoint) if self.entrypoint else None
            job_dict["image"] = (self.image,)
            job_dict["memory"] = (self.resources.memory,)
            job_dict["cpu"] = self.resources.cpu
        return job_dict

    def to_json(self):
        """
        Convert the Job instance to a JSON string representation.
        """
        return json.dumps(self.to_dict())

    def verify_repo_is_ready(self) -> Tuple[bool, str]:
        is_committed = (
            subprocess.run(
                ("git diff --exit-code"), shell=True, capture_output=True
            ).returncode
            == 0
        )
        if not is_committed:
            return (
                False,
                "Uncommitted changes detected. Please commit your changes before running the job.",
            )

        local_commit = subprocess.run(
            ("git rev-parse HEAD"), shell=True, capture_output=True, text=True
        ).stdout.strip()
        remote_commit = (
            subprocess.run(
                ("git ls-remote origin HEAD"),
                shell=True,
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\t")[0]
        )

        if local_commit != remote_commit:
            return (
                False,
                "Local commit does not match remote HEAD. Please pull the latest changes before running the job.",
            )

        branch = subprocess.run(
            ("git rev-parse --abbrev-ref HEAD"),
            shell=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return True, ""

    def run(self) -> Tuple[bool, str]:
        """
        Run the job. This method should be implemented to execute the job logic.
        It verifies the repository state and prepares the job for execution.
        Returns a tuple of (success: bool, message: str).
        If the repository is not ready, it returns False with an error message.
        If the job runs successfully, it returns True with an empty message.
        """
        if is_dt_installed():
            check_result = self.verify_repo_is_ready()
            if not check_result[0]:
                raise RepoValidationError(check_result[1])
            logger.info(
                f"Running job '{self.name}' in environment '{self.environment}' as '{self.run_as}'"
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                temp_file.write(self.to_json().encode())

            dt__Job().run(f"file://{temp_file.name}")
            os.remove(temp_file.name)

            return True, ""
        else:
            raise NotImplementedError(
                "DataTailr is not installed. Please install DataTailr to run this job."
            )
