# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from datatailr.wrapper import (
    dt__Blob,
    dt__Dns,
    dt__Email,
    dt__Group,
    dt__Job,
    dt__Kv,
    dt__Log,
    dt__Node,
    dt__Registry,
    dt__Service,
    dt__Settings,
    dt__Sms,
    dt__System,
    dt__Tag,
    dt__User,
    mock_cli_tool,
)
from datatailr.group import Group
from datatailr.user import User
from datatailr.acl import ACL
from datatailr.blob import Blob
from datatailr.build import Image
from datatailr.dt_json import dt_json
from datatailr.utils import Environment, is_dt_installed
from datatailr.version import __version__

system = dt__System()
if isinstance(system, mock_cli_tool):
    __provider__ = "not installed"
else:
    __provider__ = system.provider()

__all__ = [
    "ACL",
    "Blob",
    "Environment",
    "Group",
    "Image",
    "User",
    "__version__",
    "__provider__",
    "dt__Blob",
    "dt__Dns",
    "dt__Email",
    "dt__Group",
    "dt__Job",
    "dt__Kv",
    "dt__Log",
    "dt__Node",
    "dt__Registry",
    "dt__Service",
    "dt__Settings",
    "dt__Sms",
    "dt__System",
    "dt__Tag",
    "dt__User",
    "dt_json",
    "is_dt_installed",
]
