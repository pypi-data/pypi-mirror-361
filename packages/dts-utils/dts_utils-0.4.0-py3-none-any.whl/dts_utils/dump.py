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

from pathlib import Path
from typing import Optional

from .__version__ import __version__
from .dts import Dts
from .node import Node


def dump(dts: Dts, node_name: Optional[str], status: bool = False) -> str:
    dump_str: str = ""

    if not node_name:
        if status:
            for n in dts._dt.node_iter():
                node = Node(n)
                if node.status and node.status == "okay":
                    if node.compatible and "clock" not in node.compatible:
                        dump_str += str(node._node) + "\n"
        else:
            dump_str += str(dts._dt)
    else:
        node = getattr(dts, node_name)
        if node:
            dump_str += str(node._node)
        else:
            raise ValueError(f"{node_name} not found in dts file")

    return dump_str.strip("\n")


def main() -> None:
    import argparse
    from rich import print, traceback

    traceback.install()

    parser = argparse.ArgumentParser(
        prog="dts_dump", description="dump a dts in a human readable format"
    )

    parser.add_argument("dts", type=Path, help="dts file")
    parser.add_argument(
        "node", nargs="?", type=str, default=None, help="filter on node name or label"
    )
    parser.add_argument(
        "-s",
        "--status-okay",
        action="store_true",
        help="dump only status=okay nodes, except clocks",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )
    args = parser.parse_args()

    dts = Dts(args.dts.resolve(strict=True))
    s = dump(dts, args.node, args.status_okay)
    print(s)
