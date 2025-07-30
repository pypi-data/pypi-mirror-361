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

from devicetree import dtlib  # type: ignore
from typing import Any, Optional


class Node:
    def __init__(self, node: dtlib.Node):
        self._node = node

    @property
    def name(self):
        return self._node.name

    @property
    def label(self):
        if len(self._node.labels) > 0:
            return self._node.labels[0]
        return ""

    @property
    def parent(self):
        return self._node.parent

    @property
    def unit_addr(self):
        return self._node.unit_addr

    def __getattr__(self, __name: str) -> Any:
        from .property import Property

        if __name in self._node.nodes:
            return Node(self._node.nodes[__name])
        elif __name in self._node.dt.label2node:
            return Node(self._node.dt.label2node[__name])
        elif __name in self._node.props:
            prop = self._node.props[__name]
            return Property(prop).value

    def get_interrupt_parent(self) -> Optional["Node"]:
        from .property import Property

        _node = self._node
        interrupt_parent = None

        while _node:
            if "interrupt-parent" in _node.props:
                interrupt_parent = Property(_node.props["interrupt-parent"]).value
                break
            else:
                _node = _node.parent

        return interrupt_parent
