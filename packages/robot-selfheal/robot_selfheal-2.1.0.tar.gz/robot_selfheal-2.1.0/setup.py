#!/usr/bin/env python3
"""Setup script for Robot Framework Self-Healing Library."""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Robot Framework Self-Healing Library for automated test maintenance"

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="robot-selfheal",
    version="2.1.0",
    author="Samarth Math, Vikas Gupta, Onkar Pawar",
    author_email="samarth.math@indexnine.com, vikas.gupta@indexnine.com, onkar.pawar@indexnine.com",
    description="Robot Framework Self-Healing Library for automated test maintenance",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/samarthindex9/selfhealing_library/tree/pypi-packaging",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "robot_selfheal": ["config.json"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: Acceptance",
        "Topic :: Software Development :: Testing :: Unit",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
        "Framework :: Robot Framework :: Tool",
        "Environment :: Console",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "robot-selfheal=robot_selfheal.cli:main",
        ],
        "robot.libraries": [
            "SelfHeal=robot_selfheal:SelfHeal",
        ],
        "robot.listeners": [
            "SelfHealListener=robot_selfheal:SelfHealListener",
        ],
    },
    keywords="robotframework selenium testing automation self-healing locator web-testing ai machine-learning test-automation quality-assurance xpath ui-testing",
    project_urls={
        "Bug Reports": "https://github.com/samarthindex9/selfhealing_library/tree/pypi-packaging",
        "Source": "https://github.com/samarthindex9/selfhealing_library/tree/pypi-packaging",
        "Documentation": "https://github.com/samarthindex9/selfhealing_library/tree/pypi-packaging",
    },
) 