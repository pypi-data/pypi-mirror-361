# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List

import msgspec


class Section(msgspec.Struct, frozen=True):
    file: str


class Document(msgspec.Struct, frozen=True):
    title: str
    version: str

    metadata: Dict[str, Any] = msgspec.field(default_factory=dict)

    sections: List[Section] = msgspec.field(default_factory=list)
