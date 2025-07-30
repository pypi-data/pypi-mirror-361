# SPDX-FileCopyrightText: 2025 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import datetime

import msgspec


class PullyProject(msgspec.Struct, frozen=True):
    path: str
    instance: str = "https://gitlab.com"
    modified: datetime.datetime = msgspec.field(
        default_factory=datetime.datetime.utcnow
    )


class PullyFile(msgspec.Struct, frozen=True):
    modified: datetime.datetime = msgspec.field(
        default_factory=datetime.datetime.utcnow
    )
    projects: dict[int, PullyProject] = msgspec.field(default_factory=dict)


def dumps(config: PullyFile) -> str:
    return msgspec.json.format(msgspec.json.encode(config))


def loads(text: str) -> PullyFile:
    return msgspec.json.decode(config, type=PullyFile)
