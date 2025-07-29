# -*- encoding: utf-8 -*-
# @Author: SWHL
# @Contact: liekkaskono@163.com
import os
import sys
from pathlib import Path
from typing import List, Union

import setuptools
from get_pypi_latest_version import GetPyPiLatestVersion


def read_txt() -> List[str]:
    with open("requirements.txt", encoding="utf8") as f:
        return f.read().splitlines()


def get_readme():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base_dir, "README.md"), encoding="utf-8") as f:
        return f.read()


MODULE_NAME = "rapidocr"

obtainer = GetPyPiLatestVersion()
try:
    latest_version = obtainer(MODULE_NAME)
except Exception as e:
    latest_version = "0.0.0"
VERSION_NUM = obtainer.version_add_one(latest_version, add_patch=True)

if len(sys.argv) > 2:
    match_str = " ".join(sys.argv[2:])
    matched_versions = obtainer.extract_version(match_str)
    if matched_versions:
        VERSION_NUM = matched_versions
sys.argv = sys.argv[:2]

project_urls = {
    "Documentation": "https://rapidai.github.io/RapidOCRDocs",
    "Changelog": "https://github.com/RapidAI/RapidOCR/releases",
}

setuptools.setup(
    name="rapidocr-glock-fei",
    version="3.2.3",
    platforms="Any",
    description="Awesome OCR Library",
    long_description=get_readme(),
    long_description_content_type="text/markdown",
    author="SWHL",
    author_email="liekkaskono@163.com",
    url="https://github.com/RapidAI/RapidOCR",
    project_urls=project_urls,
    license="Apache-2.0",
    include_package_data=True,
    install_requires=read_txt(),
    package_dir={"": MODULE_NAME},
    packages=setuptools.find_namespace_packages(where=MODULE_NAME),
    package_data={"": ["*.onnx", "*.yaml", "*.txt"]},
    keywords=[
        "ocr,text_detection,text_recognition,db,onnxruntime,paddleocr,openvino,rapidocr"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.6,<4",
    entry_points={
        "console_scripts": [f"{MODULE_NAME}={MODULE_NAME}.main:main"],
    },
)
