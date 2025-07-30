from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from tuspyserver.router import TusRouterOptions

import datetime
import os
from typing import Type, TypeVar
from uuid import uuid4

from tuspyserver.info import TusUploadInfo
from tuspyserver.params import TusUploadParams

# Type variable for custom parameter types
T = TypeVar('T', bound=TusUploadParams)


class TusUploadFile:
    uid: str
    _info: TusUploadInfo
    _options: TusRouterOptions

    def __init__(
        self,
        options: TusRouterOptions,
        uid: str | None = None,
        params: TusUploadParams | None = None,
        param_class: Type[TusUploadParams] = TusUploadParams,
    ):
        self._options = options
        # init
        if uid is None:
            # creating new file
            self.uid = str(uuid4().hex)
            self.create()
        else:
            # reading existing file
            self.uid = uid
        # create the files dir if necessary
        if not os.path.exists(self._options.files_dir):
            os.makedirs(self._options.files_dir)
        # instantiate upload info with custom parameter class
        self._info = TusUploadInfo(file=self, params=params, param_class=param_class)

    @property
    def path(self) -> str:
        return os.path.join(self._options.files_dir, f"{self.uid}")

    @property
    def options(self) -> TusRouterOptions:
        return self._options

    @property
    def info(self) -> TusUploadParams | None:
        return self._info.params

    @info.setter
    def info(self, value) -> None:
        self._info.params = value

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)

    def create(self) -> None:
        open(self.path, "a").close()

    def read(self) -> bytes | None:
        if self.exists:
            with open(self.path, "rb") as f:
                return f.read()
        return None

    def delete(self, uid: str) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)

        # Only try to delete info file if info exists
        if self.info is not None and hasattr(self._info, "path"):
            if os.path.exists(self._info.path):
                os.remove(self._info.path)

    def __len__(self) -> int:
        if self.exists:
            return os.path.getsize(self.path)
        return 0

    def set_param_class(self, param_class: Type[TusUploadParams]) -> None:
        """Set a custom parameter class for this file"""
        self._info.set_param_class(param_class)


def list_files(options: TusRouterOptions) -> list[str]:
    return [f for f in os.listdir(options.files_dir) if len(f) == 32]


def gc_files(options: TusRouterOptions):
    for uid in list_files(options):
        file = TusUploadFile(uid=uid, options=options)
        if (
            file.info is not None
            and file.info.expires
            and isinstance(file.info.expires, str)
            and datetime.datetime.fromisoformat(file.info.expires)
            < datetime.datetime.now()
        ):
            file.delete(uid)
