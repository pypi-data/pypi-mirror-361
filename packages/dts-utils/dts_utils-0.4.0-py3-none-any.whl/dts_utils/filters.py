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

from typing import Optional, Any
from .exceptions import InvalidPropertyValue, InvalidTemplateValueType, InvalidPropertyValueType
from .node import Node

from .tests import is_enabled


def f_interrupts(value: Node) -> list[tuple[Node, int]]:
    """Interrupts custom jinja filter.

    This filter return the list of interrupts that belong to the given node
    Each element is a tuple with the following field:
     - parent interrupt controller phandle
     - irq num in that controller
     - (...) any additional field, controller specific,
       according to controller `#interrupt-cells` property.

    Parameters
    ----------
    value: Node
        Jinja filter left value, must be a dts node

    Returns
    -------
    list[tuple[Node, int]]
        A list element is a tuple w/ at least the interrupt parent Node and irq number.
        Number of elements packed in return tuple depends on the interrupt parent
        `#interrupt-cells` property.
        E.g. NVIC interrupt has 2 elements, irqnum and irqprio.
        If the node has no interrupts declared, the list is empty.

    Notes
    -----
    Correct type annotation for return type shall be list[tuple[Node, int, *tuple[Any, ...]]] but
    this is defined by PEP-646 and requires Python-3.11+

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
    """
    _interrupts = list()

    if not isinstance(value, Node):
        raise InvalidTemplateValueType("interrupts", type(value), Node)

    _interrupts_prop = value.interrupts
    if _interrupts_prop:
        _interrupt_parent = value.get_interrupt_parent()
        _interrupt_cells = getattr(_interrupt_parent, "#interrupt-cells")

        # walk interrupt list according to cell size
        while len(_interrupts_prop):
            _interrupts.append((_interrupt_parent, *tuple(_interrupts_prop[:_interrupt_cells])))
            _interrupts_prop = _interrupts_prop[_interrupt_cells:]

    return _interrupts


def f_owner(value: Node) -> int:
    """Owner custom jinja filter.

    This filter returns the task label that owned the device.

    Parameters
    ----------
    value: Node
        Jinja filter left value, must be a dts node

    Returns
    -------
    int
        Owner (task) label, 0 (i.e. owned by sentry kernel) by default

    Notes
    -----
    If a node is not owned, or owned by sentry kernel, property MUST NOT be present

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
    InvalidPropertyValueType
        If `sentry,owner` is not an instance of `int` type
    InvalidPropertyValue
        If `sentry,owner` is set to 0, this is a reserved value for internal kernel usage
    """
    if not isinstance(value, Node):
        raise InvalidTemplateValueType("owner", type(value), Node)

    prop = "sentry,owner"
    if prop in value._node.props:
        owner_label = getattr(value, prop)
        if not isinstance(owner_label, int):
            raise InvalidPropertyValueType(prop, value, int)
        if owner_label == 0:
            raise InvalidPropertyValue(
                prop, value, "Non zero task label (0 is reserved for kernel internal usage)"
            )
        return owner_label

    return 0


def f_peripherals(value: Node) -> list[Node]:
    """Peripherals custom jinja filter.

    This filter returns the list of child none of the given node

    Parameters
    ----------
    value: Node
        Jinja filter left value, must be a dts node

    Returns
    -------
    list[Node]
        List of child (sub) none, empty if no such subnode.

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
    """
    _peripherals = list()

    if not isinstance(value, Node):
        raise InvalidTemplateValueType("peripherals", type(value), Node)

    for child in value._node.nodes.values():
        _peripherals.append(Node(child))

    return _peripherals


def f_owned(value: list[Node]) -> list[Node]:
    """Owned custom jinja filter.

    Filters the input list and return a list of node w/ an owner (i.e. not owned by sentry kernel)

    Parameters
    ----------
    value: list[Node]
        Jinja filter left value, must be a list of dts node

    Returns
    -------
    list[Node]
        A filtered list w/ only nodes w/ `sentry,owner` different from 0

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not a list of dts node
    """
    if not isinstance(value, list):
        raise InvalidTemplateValueType("owned", type(value), list)

    return list(filter(lambda x: (f_owner(x) != 0), value))


def f_enabled(value: list[Node]) -> list[Node]:
    """Enable custom jinja filter.

    Filters the input list and return a list of node w/ `status=okay` property

    Parameters
    ----------
    value: list[Node]
        Jinja filter left value, must be a list of dts node

    Returns
    -------
    list[Node]
        A filtered list w/ only nodes w/ `status=okay`

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not a list of dts node
    """
    if not isinstance(value, list):
        raise InvalidTemplateValueType("enabled", type(value), list)

    return list(filter(lambda x: (is_enabled(x) != 0), value))


def f_has_property(value: Node, node_property: str, expected_value: Optional[Any] = None) -> bool:
    """has_property custom jinja filter.

    Returns True if given node has the property.
    Optionally, check property value to expected if given.

    Parameters
    ----------
    value: Node
        DTS node to filter
    node_property: str
        Property name
    expected_value: Optional[Any]
        Property expected value, optional

    Returns
    -------
    bool
        True if Node holds the given property
        If expected is provided, True if property value matches.
        False otherwise.

    Raises
    ------
    InvalidTemplateValueType
        if `value` is not of Node type
        if `node_property` is not of str type

    Notes
    -----
    For boolean property, no expected value is needed, in devicetree, boolean property has
    no value, present means true, false otherwise.
    """
    if not isinstance(value, Node):
        raise InvalidTemplateValueType("has_property", type(value), Node)
    if not isinstance(node_property, str):
        raise InvalidTemplateValueType("has_property", type(node_property), str)

    prop = value._node.props.get(node_property)
    if not prop:
        return False
    elif not expected_value:
        # Property found but no expected value, return True
        return True
    else:
        # Otherwise, check expected
        return prop.value == expected_value


def f_with_property(
    value: list[Node], node_property: str, expected_value: Optional[Any] = None
) -> list[Node]:
    """with_property custom jinja filter.

    Filters the input list of Node and returns the list of Node with the given property

    Parameters
    ----------
    value: list[Node]
        DTS node list to filter
    node_property: str
        Property name
    expected_value: Optional[Any]
        Property expected value, optional

    Returns
    -------
    list[Node]
        A filtered list w/ only nodes w/ `property_name` (optionally equals to expected)

    Raises
    ------
    InvalidTemplateValueType
        if `value` is not of Node type
        if `node_property` is not of str type
    """
    if not isinstance(value, list):
        raise InvalidTemplateValueType("with_property", type(value), list)
    if not isinstance(node_property, str):
        raise InvalidTemplateValueType("with_property", type(node_property), str)

    return list(
        filter(lambda node: (f_has_property(node, node_property, expected_value) != 0), value)
    )
