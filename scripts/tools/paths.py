"""
mbed SDK
Copyright (c) 2011-2013 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from os.path import join
from os import getenv

# Conventions about the directory structure
from tools.settings import ROOT, BUILD_DIR

# Allow overriding some of the build parameters using environment variables
BUILD_DIR = getenv("MBED_BUILD_DIR") or BUILD_DIR

# Embedded Libraries Sources
LIB_DIR = join(ROOT, "features/unsupported")

TOOLS = join(ROOT, "tools")
TOOLS_DATA = join(TOOLS, "data")
TOOLS_BOOTLOADERS = join(TOOLS, "bootloaders")

# mbed libraries
MBED_HEADER = join(ROOT, "mbed.h")
MBED_DRIVERS = join(ROOT, "drivers")
MBED_PLATFORM = join(ROOT, "platform")
MBED_HAL = join(ROOT, "hal")

MBED_CMSIS_PATH = join(ROOT, "cmsis")
MBED_TARGETS_PATH = join(ROOT, "targets")


# Export
EXPORT_DIR = join(BUILD_DIR, "export")
EXPORT_WORKSPACE = join(EXPORT_DIR, "workspace")
EXPORT_TMP = join(EXPORT_DIR, ".temp")
