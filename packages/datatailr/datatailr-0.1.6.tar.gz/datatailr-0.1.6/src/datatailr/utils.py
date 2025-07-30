# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

import shutil
from enum import Enum


class Environment(Enum):
    """
    Enum representing different environments for DataTailr jobs.
    """

    DEV = "dev"
    PRE = "pre"
    PROD = "prod"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Environment.{self.name}('{self.value}')"


def is_dt_installed():
    """
    Check if DataTailr is installed by looking for the 'dt' command in the system PATH.
    """
    return shutil.which("dt") is not None
