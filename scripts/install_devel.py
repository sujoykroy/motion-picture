#!/usr/bin/env python3
"""This script will install img2vid package in editable mode.
It should be used only for development purpose."""

import pip
import os

THIS_DIR  = os.path.abspath(os.path.dirname(__file__))
pip.main([
    "install",
    "-e",
    os.path.join(THIS_DIR, ".."),
])