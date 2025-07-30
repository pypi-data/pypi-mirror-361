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

from .exceptions import InvalidTemplateValueType
from .node import Node


def is_enabled(value: Node) -> bool:
    """Enable custom jinja test.

    Custom jinja test that return true if Node is enabled, i.e. `status=okay`

    Parameters
    ----------
    value: Node
        Jinja test left value, must be a dts node

    Returns
    -------
    bool
        True if `status` property equals `okay`, False otherwise

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
    """
    if not isinstance(value, Node):
        raise InvalidTemplateValueType("is_enabled", type(value), Node)
    status = getattr(value, "status")

    if status:
        return True if status == "okay" else False

    return False


def is_owned(value: Node) -> bool:
    """Owned custom jinja test.

    Custom jinja test that return true if Node has a valid `sentry,owner` property

    Parameters
    ----------
    value: Node
        Jinja test left value, must be a dts node

    Returns
    -------
    bool
        True if `sentry,owner` is valid

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
    """
    from .filters import f_owner

    if not isinstance(value, Node):
        raise InvalidTemplateValueType("is_owned", type(value), Node)
    return f_owner(value) != 0


def is_owned_by(value: Node, label: int) -> bool:
    """Owned_by custom jinja test.

    Custom jinja test that return true if Node owner `sentry,owner` matches the given one

    Parameters
    ----------
    value: Node
        Jinja test left value, must be a dts node
    label: int
        Owner label to check

    Returns
    -------
    bool
        True if `sentry,owner` equals `label` parameter, False otherwise

    Raises
    ------
    InvalidTemplateValueType
        If `value` parameter is not an instance of dts node
        If `label` parameter is not an integer
    """
    if not isinstance(value, Node):
        raise InvalidTemplateValueType("is_owned_by", type(value), Node)

    if not isinstance(label, int):
        raise InvalidTemplateValueType("is_owned_by", type(label), int)

    from .filters import f_owner

    return f_owner(value) == label
