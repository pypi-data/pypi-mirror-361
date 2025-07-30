# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from datatailr.logging import DatatailrLogger
from datatailr.scheduler import batch

logger = DatatailrLogger(__name__).get_logger()


@batch()
def foo():
    logger.info(f"Running foo from {__name__}")
    return "Hello from foo in test_submodule"


@batch()
def test_function(a, b, rundate=None):
    """Test function for the submodule."""
    logger.info(f"Running test_function from test_submodule, {__name__}")
    logger.info(f"Arguments: a={a}, b={b}, rundate={rundate}")

    return f"args: ({a}, {b}, {rundate}), kwargs: {{}}"


@batch()
def another_test_function(x, y, z=None, rundate=None):
    """Another test function for the submodule."""
    logger.info(f"Running another_test_function from test_submodule, {__name__}")
    logger.info(f"Arguments: x={x}, y={y}, z={z}, rundate={rundate}")

    return f"args: ({x}, {y}, {z}), kwargs: {{}}"
