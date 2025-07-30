# SPDX-FileCopyrightText: 2025 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import datetime
from pathlib import Path

import msgspec

from .constants import PULLY_FILE_NAME


class PullyProject(msgspec.Struct, frozen=True):
    project_id: int
    local_path: str
    ssh_url: str
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


def dump(config: PullyFile, root_path: Path) -> str:
    with open(root_path / PULLY_FILE_NAME, "wb") as handle:
        handle.write(dumps(config))


def loads(text: str) -> PullyFile:
    return msgspec.json.decode(text, type=PullyFile)


def load(root_path: Path) -> PullyFile:
    try:
        with open(root_path / PULLY_FILE_NAME, "rb") as handle:
            return loads(handle.read())
    except FileNotFoundError:
        return PullyFile()
