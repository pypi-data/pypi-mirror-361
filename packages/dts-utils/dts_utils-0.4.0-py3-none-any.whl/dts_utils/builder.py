# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2024 Ledger SAS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path
from types import ModuleType

from jinja2 import Environment, FileSystemLoader

from .__version__ import __version__
from .dts import Dts
from . import filters
from . import tests


def process(dts: Dts, input: Path, output: Path) -> None:
    def _add_to_jinja2_env_dict(d: dict, prefix: str, mod: ModuleType) -> None:
        """Add callable from a given module to specified jinja env dict.

        Callable must be prefixed to ease insertion and avoid duplication

        Notes
        -----
        Internal private function

        Parameters
        ----------
        d: dict
            Jinja2 environment dictionary to use, e.g. filters (resp. tests) for custom filters
            (reps. tests)
        prefix: str
            Prefix used to look for callable, e.g. by convention, custom filters are prefixed by
            `f_`
        mod: ModuleType
            Python module to inspect
        """
        for key, val in mod.__dict__.items():
            if callable(val) and key.startswith(prefix):
                d[key[len(prefix) :]] = val

    environment = Environment(
        loader=FileSystemLoader(searchpath=input.parent),
        extensions=["jinja2.ext.loopcontrols"],
    )

    _add_to_jinja2_env_dict(environment.filters, "f_", filters)
    _add_to_jinja2_env_dict(environment.tests, "is_", tests)

    template = environment.get_template(input.name)

    with output.open("w", encoding="utf-8") as outfile:
        outfile.write(template.render(dts=dts, env=os.environ))


def main() -> None:
    import argparse
    import rich.traceback

    rich.traceback.install(max_frames=2)

    parser = argparse.ArgumentParser(
        prog="dts2src", description="render jinja2 template using dts as data source"
    )
    parser.add_argument(
        "-d",
        "--dts",
        required=True,
        action="store",
        type=Path,
        help="dts file to use as data source",
    )
    parser.add_argument(
        "-t",
        "--template",
        required=True,
        action="store",
        type=Path,
        help="source template in jinja2 syntax",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    parser.add_argument("output", type=Path, help="output filename")
    args = parser.parse_args()

    process(Dts(args.dts.resolve(strict=True)), args.template, args.output)
