"""The generic interface for all exporters.
"""

from __future__ import print_function, division, absolute_import

import sys
from os.path import join, abspath, dirname, exists
from os.path import basename, relpath, normpath, splitext
from os import makedirs
import copy


from ..build_api import prepare_toolchain, scan_resources
from ..toolchains import Resources
from ..targets import TARGET_NAMES
from . import (uvision)

EXPORTERS = {
    u'uvision5': uvision.Uvision,
    u'uvision': uvision.Uvision,
}

ERROR_MESSAGE_UNSUPPORTED_TOOLCHAIN = """
Sorry, the target %s is not currently supported on the %s toolchain.
Please refer to <a href='/handbook/Exporting-to-offline-toolchains' target='_blank'>Exporting to offline toolchains</a> for more information.
"""

ERROR_MESSAGE_NOT_EXPORT_LIBS = """
To export this project please <a href='http://mbed.org/compiler/?import=http://mbed.org/users/mbed_official/code/mbed-export/k&mode=lib' target='_blank'>import the export version of the mbed library</a>.
"""

def mcu_ide_list():
    """Shows list of exportable ides 

    """
    supported_ides = sorted(EXPORTERS.keys())
    return "\n".join(supported_ides)


def mcu_ide_matrix(verbose_html=False):
    """Shows target map using prettytable

    Keyword argumets:
    verbose_html - print the matrix in html format
    """
    supported_ides = sorted(EXPORTERS.keys())
    # Only use it in this function so building works without extra modules
    from prettytable import PrettyTable, ALL

    # All tests status table print
    table_printer = PrettyTable(["Platform"] + supported_ides)
    # Align table
    for col in supported_ides:
        table_printer.align[col] = "c"
    table_printer.align["Platform"] = "l"

    perm_counter = 0
    for target in sorted(TARGET_NAMES):
        row = [target]  # First column is platform name
        for ide in supported_ides:
            text = "-"
            if EXPORTERS[ide].is_target_supported(target):
                if verbose_html:
                    text = "&#10003;"
                else:
                    text = "x"
                perm_counter += 1
            row.append(text)
        table_printer.add_row(row)

    table_printer.border = True
    table_printer.vrules = ALL
    table_printer.hrules = ALL
    # creates a html page in a shorter format suitable for readme.md
    if verbose_html:
        result = table_printer.get_html_string()
    else:
        result = table_printer.get_string()
    result += "\n"
    result += "Total IDEs: %d\n"% (len(supported_ides))
    if verbose_html:
        result += "<br>"
    result += "Total platforms: %d\n"% (len(TARGET_NAMES))
    if verbose_html:
        result += "<br>"
    result += "Total permutations: %d"% (perm_counter)
    if verbose_html:
        result = result.replace("&amp;", "&")
    return result


def get_exporter_toolchain(ide):
    """ Return the exporter class and the toolchain string as a tuple

    Positional arguments:
    ide - the ide name of an exporter
    """
    return EXPORTERS[ide], EXPORTERS[ide].TOOLCHAIN


def generate_project_files(resources, export_path, target, name, toolchain, ide,
                           macros=None):
    """Generate the project files for a project

    Positional arguments:
    resources - a Resources object containing all of the files needed to build
      this project
    export_path - location to place project files
    name - name of the project
    toolchain - a toolchain class that corresponds to the toolchain used by the
      IDE or makefile
    ide - IDE name to export to

    Optional arguments:
    macros - additional macros that should be defined within the exported
      project
    """
    exporter_cls, _ = get_exporter_toolchain(ide)
    exporter = exporter_cls(target, export_path, name, toolchain,
                            extra_symbols=macros, resources=resources)
    exporter.generate()
    files = exporter.generated_files
    return files, exporter

def export_project(src_paths, export_path, target, ide, libraries_paths=None,
                   linker_script=None, notify=None, name=None, inc_dirs=None,
                   jobs=1, config=None, macros=None, zip_proj=None,
                   inc_repos=False, build_profile=None, app_config=None,
                   ignore=None):
    """Generates a project file and creates a zip archive if specified

    Positional Arguments:
    src_paths - a list of paths from which to find source files
    export_path - a path specifying the location of generated project files
    target - the mbed board/mcu for which to generate the executable
    ide - the ide for which to generate the project fields

    Keyword Arguments:
    libraries_paths - paths to additional libraries
    linker_script - path to the linker script for the specified target
    notify - function is passed all events, and expected to handle notification
      of the user, emit the events to a log, etc.
    name - project name
    inc_dirs - additional include directories
    jobs - number of threads
    config - toolchain's config object
    macros - User-defined macros
    zip_proj - string name of the zip archive you wish to creat (exclude arg
     if you do not wish to create an archive
    ignore - list of paths to add to mbedignore
    """

    # Convert src_path to a list if needed
    if isinstance(src_paths, dict):
        paths = sum(src_paths.values(), [])
    elif isinstance(src_paths, list):
        paths = src_paths[:]
    else:
        paths = [src_paths]

    # Extend src_paths wit libraries_paths
    if libraries_paths is not None:
        paths.extend(libraries_paths)

    if not isinstance(src_paths, dict):
        src_paths = {"": paths}

    # Export Directory
    if not exists(export_path):
        makedirs(export_path)

    _, toolchain_name = get_exporter_toolchain(ide)
    print('toolchain_name:' + str(toolchain_name))
    print('ide:' + str(ide))

    # Pass all params to the unified prepare_resources()
    toolchain = prepare_toolchain(
        paths, "", target, toolchain_name, macros=macros, jobs=jobs,
        notify=notify, config=config, build_profile=build_profile,
        app_config=app_config, ignore=ignore)

    toolchain.RESPONSE_FILES = False
    if name is None:
        name = basename(normpath(abspath(src_paths[0])))

    for loc, path in src_paths.items():
        resource_dict = {loc: toolchain.scan_resources_zephyr(path,
            collect_ignores=True)}

    resources = Resources()

    for loc, res in resource_dict.items():
        temp = copy.deepcopy(res)
        temp.subtract_basepath(".", loc)
        resources.add(temp)
        #print('VARUN:resources..loc:' + str(loc))
        #print('VARUN:resources.res:' + str(res))

    toolchain.build_dir = export_path
    toolchain.config.load_resources(resources)
    #toolchain.set_config_data(toolchain.config.get_config_data())
    #config_header = toolchain.get_config_header()
    #resources.headers.append(config_header)
    #resources.file_basepath[config_header] = dirname(config_header)

    # Change linker script if specified
    if linker_script is not None:
        resources.linker_script = linker_script

    files, exporter = generate_project_files(resources, export_path,
                                             target, name, toolchain, ide,
                                             macros=macros)
    #files.append(config_header)
    if zip_proj:
        for resource in resource_dict.values():
            for label, res in resource.features.items():
                resource.add(res)
        if isinstance(zip_proj, basestring):
            zip_export(join(export_path, zip_proj), name, resource_dict,
                       files + list(exporter.static_files), inc_repos, notify)
        else:
            zip_export(zip_proj, name, resource_dict,
                       files + list(exporter.static_files), inc_repos, notify)
    '''
    else:
        for static_file in exporter.static_files:
            if not exists(join(export_path, basename(static_file))):
                copyfile(static_file, join(export_path, basename(static_file)))
    '''
    return exporter
