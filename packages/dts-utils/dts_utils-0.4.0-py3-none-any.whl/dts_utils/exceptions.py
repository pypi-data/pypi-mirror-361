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

from typing import Any, Optional, cast
from inspect import stack
from pathlib import Path
import sys

from jinja2.environment import Template

from .node import Node


def _get_template_error_location() -> Optional[str]:
    for frameInfo in stack():
        if frameInfo.frame.f_globals.get("__jinja_template__") is not None:
            template = cast(Template, frameInfo.frame.f_globals.get("__jinja_template__"))
            return f"{template.filename}:{template.get_corresponding_lineno(frameInfo.lineno)}"
    return None


class OutpostDeviceTreeException(Exception):
    def __init__(self, message) -> None:
        template = _get_template_error_location()
        self.message = str()
        if template:
            self.message += f"{Path(sys.argv[0]).name} error while rendering template {template}"
        self.message += message
        super().__init__(self.message)


class InvalidTemplateValueType(OutpostDeviceTreeException):
    def __init__(self, name: str, actual: type, expected: type) -> None:
        self.message = f"""
In {name}, invalid value type, got {actual.__name__}, expected {expected.__name__}
        """
        super().__init__(self.message)


class InvalidPropertyValueType(OutpostDeviceTreeException):
    def __init__(self, name: str, parent: Node, expected: type) -> None:
        self.message = f"""
Property '{name}' (dts node {parent._node.path}) invalid value type
 - got: {type(getattr(parent, name))}
 - expected: {expected}"""
        super().__init__(self.message)


class InvalidPropertyValue(OutpostDeviceTreeException):
    def __init__(self, name: str, parent: Node, expected: Any) -> None:
        self.message = f"""
Property '{name}' (dts node {parent._node.path}) invalid value
 - got: {getattr(parent, name)}
 - expected: {expected}"""
        super().__init__(self.message)
