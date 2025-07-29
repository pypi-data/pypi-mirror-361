#!/usr/bin/env python
# Copyright 2018 H2O.ai;  -*- encoding: utf-8 -*-
from importlib import resources, metadata

__all__ = ["__version__", "__build_info__"]

# Build defaults
build_info = {
    "suffix": "+local",
    "build": "dev",
    "commit": "",
    "describe": "",
    "build_os": "",
    "build_machine": "",
    "build_date": "",
    "build_user": "",
    "base_version": "0.0.0",
}

if resources.is_resource("daimojo", "BUILD_INFO.txt"):
    exec(resources.read_text("daimojo", "BUILD_INFO.txt"), build_info)

# Exported properties
__version__ = metadata.version("daimojo")
__build_info__ = build_info
