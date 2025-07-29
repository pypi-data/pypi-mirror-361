from datatailr import __version__  # type: ignore
from setuptools import find_packages, setup

setup(
    name="datatailr",
    version=__version__,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    data_files=[("/datatailr/sbin", ["src/sbin/run_job.py"])],
)
