# Copyright 2023 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
"""Building this package."""

from pathlib import Path

from setuptools import find_packages, setup

from juju.version import CLIENT_VERSION

here = Path(__file__).absolute().parent
readme = here / "docs" / "readme.rst"
changelog = here / "docs" / "changelog.rst"
long_description = f"{readme.read_text()}\n\n{changelog.read_text()}"
long_description_content_type = "text/x-rst"

setup(
    name="juju",
    version=CLIENT_VERSION.strip(),
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"juju": ["py.typed"]},
    install_requires=[
        "macaroonbakery>=1.1,<2.0",
        "pyyaml>=5.1.2",
        "websockets>=13.0.1",
        "paramiko>=2.4.0",
        "pyasn1>=0.4.4",
        "toposort>=1.5,<2",
        "typing_inspect>=0.6.0",
        "kubernetes>=12.0.1,<31.0.0",
        "hvac",
        "packaging",
        "typing-extensions>=4.5.0",
        'backports.strenum>=1.3.1; python_version < "3.11"',
        "backports-datetime-fromisoformat>=2.0.2",
    ],
    extras_require={
        "dev": [
            "typing-inspect",
            "pytest",
            "pytest-asyncio <= 0.25.0",  # https://github.com/pytest-dev/pytest-asyncio/issues/1039
            "Twine",
            "freezegun",
        ]
    },
    include_package_data=True,
    maintainer="Juju Ecosystem Engineering",
    maintainer_email="juju@lists.ubuntu.com",
    description=("Python library for Juju"),
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    url="https://github.com/juju/python-libjuju",
    license="Apache 2",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    entry_points={
        "console_scripts": [],
    },
)
