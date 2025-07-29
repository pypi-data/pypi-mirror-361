# This file is part of fm-weck: executing fm-tools in containerized environments.
# https://gitlab.com/sosy-lab/software/fm-weck
#
# SPDX-FileCopyrightText: 2024 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import importlib.resources as pkg_resources
from pathlib import Path

from . import fm_tools, properties

# During the build of the wheel file, the fm-tools/data directory is copied
# to the wheel file under fm_weck/resources/fm_tools

RUN_WITH_OVERLAY = "run_with_overlay.sh"
BENCHEXEC_WHL = "BenchExec-3.25-py3-none-any.whl"
RUNEXEC_SCRIPT = "runexec"


def iter_fm_data():
    for fm_data in pkg_resources.contents(fm_tools):
        with pkg_resources.path(fm_tools, fm_data) as fake_context_path:
            fm_data_path = Path(fake_context_path)
            if fm_data_path.is_file() and (fm_data_path.name.endswith(".yml") or fm_data_path.name.endswith(".yaml")):
                yield fm_data_path


def iter_properties():
    for prop in pkg_resources.contents(properties):
        with pkg_resources.path(properties, prop) as fake_context_path:
            prop_path = Path(fake_context_path)
            if prop_path.is_file():
                yield prop_path
