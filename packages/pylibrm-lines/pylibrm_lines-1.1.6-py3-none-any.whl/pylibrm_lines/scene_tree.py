import json
import os
from typing import Optional, Union

from rm_api import Document, API
from rm_lines_sys import lib

from .scene_info import SceneInfo
from .exceptions import *


class SceneTree:
    uuid: bytes
    document: Optional[Document]
    page_uuid: Optional[str]
    _scene_info: Optional[SceneInfo]

    def __init__(self, uuid: bytes = b'', document: Document = None, page_uuid: str = None):
        if not lib:
            # Prevent creating new instances of scene tree if the library is missing
            raise LibMissing()
        self.uuid = uuid
        self.document = document
        self.page_uuid = page_uuid
        self._paragraphs = None
        self._renderer = None
        self._scene_info = None

    @property
    def api(self) -> Optional[API]:
        return self.document.api if self.document else None

    @classmethod
    def from_document(cls, document: Document, page_uuid: str):
        new = cls(document=document, page_uuid=page_uuid)
        page_file_uuid = f'{document.uuid}/{page_uuid}.rm'
        file = new.document.files_available.get(page_file_uuid)
        if file is None:
            raise FileNotFoundError("Could not find the lines file for this page_uuid")
        file_path = os.path.join(new.api.sync_file_path, file.hash)

        new.uuid = lib.buildTree(file_path.encode())

        if not new.uuid:
            raise FailedToBuildTree()

        return new

    @property
    def renderer(self):
        if not self._renderer:
            from .renderer import Renderer
            self._renderer = Renderer(self)
        return self._renderer

    @renderer.setter
    def renderer(self, value):
        from .renderer import Renderer
        if not isinstance(value, Renderer):
            raise TypeError("Renderer must be an instance of Renderer class")
        self._renderer = value

    @renderer.deleter
    def renderer(self):
        if self._renderer:
            self._renderer.destroy()
            self._renderer = None

    def to_json_file(self, output_file: Union[os.PathLike, str]):
        success = lib.convertToJsonFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToJson()

    def to_json_raw(self) -> str:
        raw = lib.convertToJson(self.uuid)
        if raw == b'':
            raise FailedToConvertToJson()
        return raw.decode()

    def to_dict(self) -> dict:
        raw = self.to_json_raw()
        return json.loads(raw)

    @property
    def scene_info(self) -> Optional[SceneInfo]:
        if not self._scene_info:
            try:
                self._scene_info = SceneInfo(self)
            except NoSceneInfo:
                return None
        return self._scene_info

    def destroy(self):
        """Destroying the scene tree will also destroy the renderer if it exists."""
        if not self.uuid:
            raise ValueError("Could not destroy tree, uuid is empty")
        del self.renderer
        lib.destroyTree(self.uuid)
        self.uuid = b''

    def __del__(self):
        """Deleting the scene tree calls the library to destroy the tree."""
        if not self.uuid:
            return
        lib.destroyTree(self.uuid)
