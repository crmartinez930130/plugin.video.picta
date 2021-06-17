# -*- coding: utf-8 -*-
# Module: dump_version
# Author: oleksis
# Created on: 16.6.2021

import json
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

PATH = Path(__file__).parent.parent

body = ""

addon_xml = PATH.joinpath("addon.xml")
tree = ET.parse(addon_xml)
root = tree.getroot()

version = root.attrib.get("version")
body = f"v{version}\n\n"

print(f"::set-output name=version::{version}")

xpath = "./extension[@point='xbmc.addon.metadata']"
ext_metadata = root.find(xpath)

changelog: Optional[ET.Element] = ext_metadata.find("news") if ext_metadata else None

if changelog is not None:
    body += str(changelog.text)

body = json.dumps(body).encode("utf-8").decode("utf-8")
print(f"::set-output name=changelog::{body}")
