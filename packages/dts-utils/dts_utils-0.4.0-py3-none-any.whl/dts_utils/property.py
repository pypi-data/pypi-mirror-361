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

from collections.abc import Iterable
from devicetree import dtlib  # type: ignore
from typing import Any

from .node import Node


class Property:
    def __init__(self, prop: dtlib.Property):
        self._prop = prop

    ValueType = {
        dtlib.Type.STRING: str,
        dtlib.Type.STRINGS: (list[str], str),
        dtlib.Type.NUM: int,
        dtlib.Type.NUMS: (list[int], int),
        dtlib.Type.PHANDLE: Node,
        dtlib.Type.PHANDLES: (list[Node], Node),
        dtlib.Type.PHANDLES_AND_NUMS: (tuple[Node, int], Node, int),
    }  # type: ignore

    @property
    def value(self) -> Any:
        if self._prop.type in self.ValueType:
            value_type = self.ValueType[self._prop.type]  # type: ignore
            value_type_str: str = (
                value_type.__name__  # type: ignore
                if not isinstance(value_type, Iterable)
                else "_".join(t.__name__ for t in value_type)
            )
            return getattr(self, f"_to_{value_type_str.lower()}")()
        return None

    def _to_str(self) -> str:
        return self._prop.to_string()

    def _to_list_str(self) -> list[str]:
        return self._prop.to_strings()

    def _to_int(self) -> int:
        return self._prop.to_num()

    def _to_list_int(self) -> list[int]:
        return self._prop.to_nums()

    def _to_node(self) -> Node:
        return Node(self._prop.to_node())

    def _to_list_node(self) -> list[Node]:
        nodes: list[Node] = []
        for n in self._prop.to_nodes():
            nodes.append(Node(n))
        return nodes

    def _to_tuple_node_int(self) -> tuple:
        assert len(self._prop.value) >= 8
        val = self._prop.value
        phandle = int.from_bytes(val[0:4], "big")
        nums = tuple(
            int.from_bytes(val[i:(i + 4)], "big") for i in range(4, len(val), 4)  # fmt: skip
        )

        return (Node(self._prop.node.dt.phandle2node[phandle]), *nums)
