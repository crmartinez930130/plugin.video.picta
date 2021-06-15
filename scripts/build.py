#!/usr/bin/python
# -*- coding: utf-8 -*-
# Module: build
# Author: oleksis
# Created on: 14.6.2021

from pathlib import Path
from shutil import copytree, ignore_patterns, make_archive, rmtree

PATH = Path(__file__).parent.parent


src_dir = str(PATH)
build_dir = "build"
addon_name = "plugin.video.picta-kodi_19"
ignore = ignore_patterns(
    ".*",
    "*.zip",
    "docs",
    "scripts",
    "tests",
    "venv",
    "requirements*",
    "__pycache__",
    "debug.log",
)
addon_path = f"{src_dir}/{build_dir}/{addon_name}"

if Path(build_dir).exists():
    print("Cleaning up...")
    rmtree(build_dir)

print("Copying files...")
copytree(src_dir, addon_path, False, ignore)

print("Zipping plugin...")
make_archive(addon_name, "zip", str(Path(addon_path).parent))

print("Build finished!")
