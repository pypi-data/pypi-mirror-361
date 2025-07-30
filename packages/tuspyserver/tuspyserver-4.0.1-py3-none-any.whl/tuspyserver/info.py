from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from tuspyserver.file import TusUploadFile

import json
import os
from typing import Type, TypeVar

from tuspyserver.params import TusUploadParams

# Type variable for custom parameter types
T = TypeVar('T', bound=TusUploadParams)


class TusUploadInfo:
    _params: TusUploadParams | None
    file: TusUploadFile
    _param_class: Type[TusUploadParams]

    def __init__(
        self, 
        file: TusUploadFile, 
        params: TusUploadParams | None = None,
        param_class: Type[TusUploadParams] = TusUploadParams
    ):
        self.file = file
        self._params = params
        self._param_class = param_class
        # create if doesn't exist
        if params and not self.exists:
            self.serialize()

    @property
    def params(self):
        self.deserialize()
        return self._params

    @params.setter
    def params(self, value):
        self._params = value
        self.serialize()

    @property
    def path(self) -> str:
        return os.path.join(self.file.options.files_dir, f"{self.file.uid}.info")

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)

    def serialize(self) -> None:
        with open(self.path, "w") as f:
            json_string = json.dumps(
                self._params, indent=4, default=lambda k: k.__dict__
            )
            f.write(json_string)

    def deserialize(self) -> TusUploadParams | None:
        if self.exists:
            try:
                with open(self.path, "r") as f:
                    content = f.read().strip()
                    if not content:  # Handle empty files
                        return None
                    json_dict = json.loads(content)
                    if json_dict:  # Only create params if we have valid data
                        # Use the custom parameter class if provided
                        self._params = self._param_class(**json_dict)
                    else:
                        self._params = None
            except (json.JSONDecodeError, FileNotFoundError, KeyError, TypeError):
                # Handle corrupted JSON or missing required fields
                self._params = None
        else:
            self._params = None

        return self._params

    def set_param_class(self, param_class: Type[TusUploadParams]) -> None:
        """Set a custom parameter class for deserialization"""
        self._param_class = param_class
