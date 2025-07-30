import pathlib
from setuptools import setup, find_packages
import re

README = (pathlib.Path(__file__).parent / "README.md").read_text()

PACKAGE_NAME = "andytele"
VERSION = "1.0.2"
SOURCE_DIRECTORY = "src"

with open("requirements.txt") as data:
    requirements = [
        line for line in data.read().split("\n") if line and not line.startswith("#")
    ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license="MIT",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="",
    author_email="",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
    ],
    keywords=[],
    include_package_data=True,
    packages=[PACKAGE_NAME, PACKAGE_NAME+'.td', PACKAGE_NAME+'.tl'],
    package_dir={PACKAGE_NAME: SOURCE_DIRECTORY},
    install_requires=requirements,
)
