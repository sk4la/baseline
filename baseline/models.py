# Copyright (C) 2021  sk4la <sk4la.box@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import abc
import enum
import logging
import pathlib
import platform
import re
import typing

from baseline import errors, schema

__all__: typing.Tuple[str, ...] = (
    "Extractor",
    "Kind",
)


@enum.unique
class Kind(str, enum.Enum):
    FILE: int = enum.auto()
    DIRECTORY: int = enum.auto()
    SYMLINK: int = enum.auto()
    BLOCK_DEVICE: int = enum.auto()
    CHARACTER_DEVICE: int = enum.auto()
    FIFO: int = enum.auto()
    SOCKET: int = enum.auto()
    MOUNT: int = enum.auto()
    OTHER: int = enum.auto()

    def __str__(self):
        return self.name.lower()


class Extractor(abc.ABC):
    """Abstract class used to derive all extractors."""

    EXTENSION_FILTERS: typing.Tuple[str, ...] = tuple()
    KINDS: typing.Tuple[int, ...] = (
        Kind.FILE,
        Kind.DIRECTORY,
        Kind.SYMLINK,
        Kind.BLOCK_DEVICE,
        Kind.CHARACTER_DEVICE,
        Kind.FIFO,
        Kind.SOCKET,
        Kind.MOUNT,
        Kind.OTHER,
    )
    MAGIC_SIGNATURE_FILTERS: typing.Tuple[str, ...] = tuple()
    SYSTEM_FILTERS: typing.Tuple[str, ...] = tuple()

    @property
    @abc.abstractmethod
    def KEY(self) -> str:
        ...

    @property
    @classmethod
    def is_compatible(cls: object) -> bool:
        return any(re.match(pattern, platform.system()) for pattern in cls.SYSTEM_FILTERS)

    @classmethod
    def supports(
        cls: object,
        entry: pathlib.Path,
        kind: int = Kind.FILE,
        magic_signature: typing.Optional[str] = None,
    ) -> bool:
        if kind not in cls.KINDS:
            return False

        filters: typing.List[bool] = [
            any(re.match(pattern, entry.suffix) for pattern in cls.EXTENSION_FILTERS),
        ]

        if magic_signature:
            filters.append(
                any(re.match(pattern, magic_signature) for pattern in cls.MAGIC_SIGNATURE_FILTERS),
            )

        return any(filters)

    def __init__(
        self: object,
        entry: pathlib.Path,
        kind: typing.Optional[int] = Kind.FILE,
        remap: typing.Dict[pathlib.Path, pathlib.Path] = {},
    ) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)

        self.entry: pathlib.Path = entry
        self.kind: typing.Optional[int] = kind
        self.remap: typing.Dict[pathlib.Path, pathlib.Path] = remap

    def remap_location(self: object, location: pathlib.Path) -> pathlib.Path:
        for source, destination in self.remap.items():
            try:
                location: pathlib.Path = destination / location.relative_to(source)

            except ValueError:
                pass

        return location

    @abc.abstractmethod
    def run(self: object, record: schema.Record) -> None:
        ...
