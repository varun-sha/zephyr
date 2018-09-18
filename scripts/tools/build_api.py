"""
mbed SDK
Copyright (c) 2011-2016 ARM Limited

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
from __future__ import print_function, division, absolute_import
from .utils import ( NotSupportedException)
from .targets import TARGET_NAMES, TARGET_MAP
from .toolchains import TOOLCHAIN_CLASSES
from .config import Config


def get_config(src_paths, target, toolchain_name, app_config=None):
    """Get the configuration object for a target-toolchain combination

    Positional arguments:
    src_paths - paths to scan for the configuration files
    target - the device we are building for
    toolchain_name - the string that identifies the build tools
    """
    # Convert src_paths to a list if needed
    if not isinstance(src_paths, list):
        src_paths = [src_paths]

    # Pass all params to the unified prepare_resources()
    toolchain = prepare_toolchain(src_paths, None, target, toolchain_name,
                                  app_config=app_config)

    # Scan src_path for config files
    resources = toolchain.scan_resources(src_paths[0])
    for path in src_paths[1:]:
        resources.add(toolchain.scan_resources(path))

    # Update configuration files until added features creates no changes
    prev_features = set()
    while True:
        # Update the configuration with any .json files found while scanning
        toolchain.config.add_config_files(resources.json_files)

        # Add features while we find new ones
        features = set(toolchain.config.get_features())
        if features == prev_features:
            break

        for feature in features:
            if feature in resources.features:
                resources += resources.features[feature]

        prev_features = features
    toolchain.config.validate_config()
    if toolchain.config.has_regions:
        _ = list(toolchain.config.regions)

    cfg, macros = toolchain.config.get_config_data()
    features = toolchain.config.get_features()
    return cfg, macros, features

ARM_COMPILERS = ("ARM", "ARMC6", "uARM")
def target_supports_toolchain(target, toolchain_name):
    if toolchain_name in ARM_COMPILERS:
        return any(tc in target.supported_toolchains for tc in ARM_COMPILERS)
    else:
        return toolchain_name in target.supported_toolchains


def prepare_toolchain(src_paths, build_dir, target, toolchain_name,
                      macros=None, clean=False, jobs=1,
                      notify=None, config=None, app_config=None,
                      build_profile=None, ignore=None):
    """ Prepares resource related objects - toolchain, target, config

    Positional arguments:
    src_paths - the paths to source directories

    Keyword arguments:
    macros - additional macros
    clean - Rebuild everything if True
    jobs - how many compilers we can run at once
    notify - Notify function for logs
    config - a Config object to use instead of creating one
    app_config - location of a chosen mbed_app.json file
    build_profile - a list of mergeable build profiles
    """

    # We need to remove all paths which are repeated to avoid
    # multiple compilations and linking with the same objects
    src_paths = [src_paths[0]] + list(set(src_paths[1:]))

    # If the configuration object was not yet created, create it now
    config = config or Config(target, src_paths, app_config=app_config)
    target = config.target
    if not target_supports_toolchain(target, toolchain_name):
        raise NotSupportedException(
            "Target {} is not supported by toolchain {}".format(
                target.name, toolchain_name))

    try:
        cur_tc = TOOLCHAIN_CLASSES[toolchain_name]
    except KeyError:
        raise KeyError("Toolchain %s not supported" % toolchain_name)

    profile = {'c': [], 'cxx': [], 'common': [], 'asm': [], 'ld': []}
    for contents in build_profile or []:
        for key in profile:
            profile[key].extend(contents[toolchain_name].get(key, []))

    toolchain = cur_tc(
        target, notify, macros, build_dir=build_dir, build_profile=profile)

    toolchain.config = config
    toolchain.jobs = jobs
    toolchain.build_all = clean

    if ignore:
        toolchain.add_ignore_patterns(root=".", base_path=".", patterns=ignore)

    return toolchain

def scan_resources(src_paths, toolchain, dependencies_paths=None,
                   inc_dirs=None, base_path=None, collect_ignores=False):
    """ Scan resources using initialized toolcain

    Positional arguments
    src_paths - the paths to source directories
    toolchain - valid toolchain object
    dependencies_paths - dependency paths that we should scan for include dirs
    inc_dirs - additional include directories which should be added to
               the scanner resources
    """

    # Scan src_path
    resources = toolchain.scan_resources(src_paths[0], base_path=base_path,
                                         collect_ignores=collect_ignores)
    for path in src_paths[1:]:
        resources.add(toolchain.scan_resources(path, base_path=base_path,
                                               collect_ignores=collect_ignores))

    # Scan dependency paths for include dirs
    if dependencies_paths is not None:
        for path in dependencies_paths:
            lib_resources = toolchain.scan_resources(path)
            resources.inc_dirs.extend(lib_resources.inc_dirs)

    # Add additional include directories if passed
    if inc_dirs:
        if isinstance(inc_dirs, list):
            resources.inc_dirs.extend(inc_dirs)
        else:
            resources.inc_dirs.append(inc_dirs)

    # Load resources into the config system which might expand/modify resources
    # based on config data
    resources = toolchain.config.load_resources(resources)

    # Set the toolchain's configuration data
    toolchain.set_config_data(toolchain.config.get_config_data())

    return resources

def get_unique_supported_toolchains(release_targets=None):
    """ Get list of all unique toolchains supported by targets

    Keyword arguments:
    release_targets - tuple structure returned from get_mbed_official_release().
                      If release_targets is not specified, then it queries all
                      known targets
    """
    unique_supported_toolchains = []

    if not release_targets:
        for target in TARGET_NAMES:
            for toolchain in TARGET_MAP[target].supported_toolchains:
                if toolchain not in unique_supported_toolchains:
                    unique_supported_toolchains.append(toolchain)
    else:
        for target in release_targets:
            for toolchain in target[1]:
                if toolchain not in unique_supported_toolchains:
                    unique_supported_toolchains.append(toolchain)

    if "ARM" in unique_supported_toolchains:
        unique_supported_toolchains.append("ARMC6")

    return unique_supported_toolchains


