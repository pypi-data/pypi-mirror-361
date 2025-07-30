# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2023 Ledger SAS
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

from devicetree import dtlib  # type: ignore
from typing import Any


from .node import Node


class Dts:
    def __init__(self, dts_file: os.PathLike) -> None:
        self._dt = dtlib.DT(str(dts_file))

    @property
    def root(self) -> Node:
        """Get root node of DTS file."""
        return Node(self._dt.root)

    def __getattr__(self, __name: str) -> Any:
        """Search for Node or Property.

        Search is done in the alias dictionary first, then in property dictionary, and finally in
        root node children.
        """
        if __name in self._dt.alias2node:
            return Node(self._dt.alias2node[__name])
        else:
            return self.root.__getattr__(__name)

    def get_compatible(self, compatible: str) -> list[Node]:
        """Return a Nodes list with the given compatible string."""
        nodes = []
        for n in self._dt.node_iter():
            node = Node(n)
            if node.compatible and compatible in node.compatible:
                nodes.append(node)
        return nodes

    def get_mappable(self) -> list[Node]:
        """Return all Nodes that declare a region."""
        nodes = []
        for n in self._dt.node_iter():
            node = Node(n)
            if node.reg and node.reg[0] != 0 and node.reg[1] > 0:
                nodes.append(node)
        return nodes

    def get_active_nodes(self) -> list[Node]:
        """Return all Nodes that are enabled."""
        nodes = []
        for n in self._dt.node_iter():
            node = Node(n)
            if node.status and node.status == "okay":
                if node.compatible and "clock" not in node.compatible:
                    nodes.append(node)
        return nodes
