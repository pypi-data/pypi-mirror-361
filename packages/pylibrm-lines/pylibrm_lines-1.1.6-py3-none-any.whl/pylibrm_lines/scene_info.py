import json
from typing import TYPE_CHECKING, Tuple, List, Optional

from rm_lines_sys import lib

from .exceptions import NoSceneInfo

if TYPE_CHECKING:
    from scene_tree import SceneTree


class SceneInfo:
    _scene_info: dict = None
    scene_tree: 'SceneTree'

    def __init__(self, scene_tree: 'SceneTree'):
        self.scene_tree = scene_tree
        self.update_scene_info()

    def get_raw(self) -> bytes:
        raw = lib.getSceneInfo(self.scene_tree.uuid)
        if raw == b'':
            raise NoSceneInfo()
        return raw

    def get_dict(self):
        return json.loads(self.get_raw().decode())

    def update_scene_info(self):
        self._scene_info = self.get_dict()

    @property
    def current_layer(self) -> str:
        return self._scene_info["currentLayer"]

    @property
    def background_visible(self) -> Optional[bool]:
        """
        This refers to the template.
        If the layer is hidden
        """
        return self._scene_info["backgroundVisible"]

    @property
    def root_document_visible(self) -> Optional[bool]:
        """
        This refers to the root text document
        If the layer is hidden in the layers or not
        """
        return self._scene_info["rootDocumentVisible"]

    @property
    def paper_size(self) -> Optional[Tuple[int, int]]:
        """
        This is a new value for the size of the page/paper as it's called by rM.
        It is used by RMPP to signal that it is larger sized. It is generally blank for RM2
        :return: Optional [w, h]
        """
        return self._scene_info["paperSize"]

    @property
    def paper_width(self) -> Optional[int]:
        """
        This a shortcut to paper_size[0]
        """
        if size := self.paper_size:
            return size[0]
        return None

    @property
    def paper_height(self) -> Optional[int]:
        """
        This a shortcut to paper_size[1]
        """
        if size := self.paper_size:
            return size[1]
        return None