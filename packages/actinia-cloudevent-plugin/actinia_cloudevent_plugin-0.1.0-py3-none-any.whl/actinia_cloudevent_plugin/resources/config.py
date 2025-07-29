#!/usr/bin/env python
"""Copyright (c) 2018-2025 mundialis GmbH & Co. KG.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Configuration file
"""

__author__ = "Carmen Tawalika, Lina Krisztian"
__copyright__ = "2018-2025 mundialis GmbH & Co. KG"
__license__ = "Apache-2.0"


import configparser
from pathlib import Path

# config can be overwritten by mounting *.ini files into folders inside
# the config folder.
DEFAULT_CONFIG_PATH = "config"
CONFIG_FILES = [
    str(f) for f in Path(DEFAULT_CONFIG_PATH).glob("**/*.ini") if f.is_file()
]
GENERATED_CONFIG = DEFAULT_CONFIG_PATH + "/actinia-cloudevent-plugin.cfg"


class EVENTRECEIVER:
    """Default config for cloudevent receiver."""

    url = "http://localhost:3000/"


class LOGCONFIG:
    """Default config for logging."""

    logfile = "actinia-cloudevent-plugin.log"
    level = "INFO"
    type = "stdout"


class Configfile:
    """Configuration file."""

    def __init__(self) -> None:
        """Overwrite config classes.

        Will overwrite the config classes above when config files
        named DEFAULT_CONFIG_PATH/**/*.ini exist.
        On first import of the module it is initialized.
        """
        config = configparser.ConfigParser()
        config.read(CONFIG_FILES)
        if len(config) <= 1:
            print("Could not find any config file, using default values.")
            return
        print("Loading config files: " + str(CONFIG_FILES) + " ...")

        with open(  # noqa: PTH123
            GENERATED_CONFIG,
            "w",
            encoding="utf-8",
        ) as configfile:
            config.write(configfile)
        print("Configuration written to " + GENERATED_CONFIG)

        # LOGGING
        if config.has_section("LOGCONFIG"):
            if config.has_option("LOGCONFIG", "logfile"):
                LOGCONFIG.logfile = config.get("LOGCONFIG", "logfile")
            if config.has_option("LOGCONFIG", "level"):
                LOGCONFIG.level = config.get("LOGCONFIG", "level")
            if config.has_option("LOGCONFIG", "type"):
                LOGCONFIG.type = config.get("LOGCONFIG", "type")

        # EVENTRECEIVER
        if config.has_section("EVENTRECEIVER"):
            if config.has_option("EVENTRECEIVER", "url"):
                EVENTRECEIVER.url = config.get("EVENTRECEIVER", "url")


init = Configfile()
