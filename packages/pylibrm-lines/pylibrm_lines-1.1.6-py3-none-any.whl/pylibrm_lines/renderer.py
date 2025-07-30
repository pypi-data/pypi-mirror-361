import json
import os
from ctypes import c_uint32
from enum import Enum
from typing import List, Optional, TYPE_CHECKING, Union, Tuple

from rm_api.defaults import DocumentTypes, FileTypes, RM_SCREEN_SIZE
from rm_lines_sys import lib

from .exceptions import FailedToConvertToMd, FailedToConvertToTxt
from .text import Paragraph
from PIL import Image

if TYPE_CHECKING:
    from .scene_tree import SceneTree


class PageType(Enum):
    Notebook = 0
    Document = 1


class SizeTracker:
    linked_layer: 'LayerInfo'
    top: int
    left: int
    bottom: int
    right: int
    frame_width: int
    frame_height: int

    def __init__(self, linked_layer: 'LayerInfo', top: int, left: int, bottom: int, right: int,
                 frame_width: int, frame_height: int):
        self._linked_layer = linked_layer
        self._top = top
        self._left = left
        self._bottom = bottom
        self._right = right
        self._frame_width = frame_width
        self._frame_height = frame_height

    @classmethod
    def from_dict(cls, linked_layer: 'LayerInfo', size_tracker_info: dict):
        return cls(
            linked_layer,
            size_tracker_info['t'],  # top
            size_tracker_info['l'],  # left
            size_tracker_info['b'],  # bottom
            size_tracker_info['r'],  # right
            size_tracker_info['fw'],  # frame_width
            size_tracker_info['fh']  # frame_height
        )

    @property
    def linked_layer(self) -> 'LayerInfo':
        return self._linked_layer

    @property
    def top(self) -> int:
        return self._top

    @property
    def left(self) -> int:
        return self._left

    @property
    def bottom(self) -> int:
        return self._bottom

    @property
    def right(self) -> int:
        return self._right

    @property
    def frame_width(self) -> int:
        return self._frame_width

    @property
    def frame_height(self) -> int:
        return self._frame_height

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


class LayerInfo:
    renderer: 'Renderer'
    uuid: str
    label: str
    visible: bool

    def __init__(self, renderer: 'Renderer', uuid: str, label: str, visible: bool = True):
        self.renderer = renderer
        self._uuid = uuid
        self._label = label
        self._visible = visible
        self._size_tracker = None

        self.update_size_tracker()

    @classmethod
    def from_dict(cls, renderer: 'Renderer', layer_info: dict):
        return cls(
            renderer,
            layer_info['groupId'],
            layer_info['label'],
            layer_info['visible']
        )

    def update_size_tracker(self):
        self._size_tracker = SizeTracker.from_dict(self, self.renderer.get_size_tracker_dict(self.uuid))

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def label(self) -> str:
        return self._label

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def size_tracker(self) -> Optional[SizeTracker]:
        if self._size_tracker is None:
            self.update_size_tracker()
        return self._size_tracker


class Renderer:
    uuid: bytes
    _paragraphs: Optional[List[Paragraph]]
    _layers: Optional[List[LayerInfo]]
    scene_tree = 'SceneTree'

    def __init__(self, scene_tree: 'SceneTree', page_type: PageType = None, landscape: bool = None):
        self.scene_tree = scene_tree
        self._paragraphs = None
        self._layers = None
        self._layers_index = {}
        if not landscape:
            if scene_tree.document:
                landscape = scene_tree.document.content.is_landscape
            else:
                raise ValueError("Missing value for landscape and cannot infer from document")
        if not page_type:
            if scene_tree.document:
                page_type = PageType.Notebook if scene_tree.document.content.file_type == FileTypes.Notebook.value else PageType.Document
            else:
                raise ValueError("Missing value for page_type and cannot infer from document type")
        self.uuid = lib.makeRenderer(self.scene_tree.uuid, page_type.value, landscape)
        self.scene_tree.renderer = self

        self._update_paragraphs()
        self._update_layers()

    @property
    def paper_size(self) -> Tuple[int, int]:
        if self.scene_tree.scene_info and self.scene_tree.scene_info.paper_size:
            return self.scene_tree.scene_info.paper_size
        else:
            return RM_SCREEN_SIZE

    def get_paragraphs_raw(self) -> Optional[bytes]:
        raw = lib.getParagraphs(self.uuid)
        if raw == b'':
            return None
        return raw

    def get_paragraphs_dict(self) -> Optional[List[dict]]:
        raw = self.get_paragraphs_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_paragraphs(self) -> Optional[List[Paragraph]]:
        paragraphs = self.get_paragraphs_dict()
        if not paragraphs:
            return None
        return [Paragraph.from_dict(self, paragraph) for paragraph in paragraphs]

    def get_layers_raw(self) -> Optional[bytes]:
        raw = lib.getLayers(self.uuid)
        if raw == b'':
            return None
        return raw

    def get_layers_dict(self) -> Optional[List[dict]]:
        raw = self.get_layers_raw()
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_layers(self) -> Optional[List[LayerInfo]]:
        layers = self.get_layers_dict()
        if not layers:
            return None
        return [LayerInfo.from_dict(self, layer) for layer in layers]

    def get_layer_by_uuid(self, layer_uuid: str) -> Optional[LayerInfo]:
        if not self._layers_index:
            self._update_layers()
        return self._layers_index.get(layer_uuid, None)

    def get_size_tracker_raw(self, layer_uuid: str) -> Optional[bytes]:
        raw = lib.getSizeTracker(self.uuid, layer_uuid.encode())
        if raw == b'':
            return None
        return raw

    def get_size_tracker_dict(self, layer_uuid: str) -> Optional[dict]:
        raw = self.get_size_tracker_raw(layer_uuid)
        if raw is None:
            return None
        return json.loads(raw.decode())

    def get_size_tracker(self, layer_uuid: str) -> Optional[SizeTracker]:
        layer = self.get_layer_by_uuid(layer_uuid)
        if not layer:
            return None
        return layer.size_tracker

    def _update_paragraphs(self):
        self._paragraphs = self.get_paragraphs()

    def _update_layers(self):
        self._layers = self.get_layers()
        self._layers_index = {layer.uuid: layer for layer in self._layers} if self._layers else {}

    @property
    def paragraphs(self) -> Optional[List[Paragraph]]:
        if self._paragraphs is None:
            self._update_paragraphs()
        return self._paragraphs

    @property
    def layers(self) -> Optional[List[LayerInfo]]:
        if self._layers is None:
            self._update_layers()
        return self._layers

    def to_md_file(self, output_file: Union[os.PathLike, str]):
        success = lib.textToMdFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToMd()

    def to_md_raw(self) -> str:
        raw = lib.textToMd(self.uuid)
        if raw == b'':
            raise FailedToConvertToMd()
        return raw.decode()

    def to_txt_file(self, output_file: Union[os.PathLike, str]):
        success = lib.textToTxtFile(self.uuid, os.fspath(output_file).encode())
        if not success:
            raise FailedToConvertToTxt()

    def to_txt_raw(self) -> str:
        raw = lib.textToTxt(self.uuid)
        if raw == b'':
            raise FailedToConvertToTxt()
        return raw.decode()

    def get_frame_raw(self, x: int, y: int, frame_width: int, frame_height: int, width: int, height: int,
                      antialias: bool = False) -> bytes:
        buffer_size = width * height
        buffer = (c_uint32 * buffer_size)()

        lib.getFrame(self.uuid, buffer, buffer_size * 4, x, y, frame_width, frame_height, width, height, antialias)
        return bytes(buffer)

    def to_image_raw(self, antialias: bool = False) -> Tuple[bytes, Tuple[int, int]]:
        return self.get_frame_raw(0, 0, *self.paper_size, *self.paper_size, antialias), self.paper_size

    def to_image(self, antialias: bool = False) -> Image.Image:
        raw_frame, size = self.to_image_raw(antialias)
        return Image.frombytes('RGBA', size, raw_frame, 'raw', 'RGBA')

    def to_image_file(self, output_file: Union[os.PathLike, str], antialias: bool = False, image_format: str = 'PNG'):
        image = self.to_image(antialias)
        image.save(os.fspath(output_file), image_format)

    def destroy(self):
        if not self.uuid:
            return
        lib.destroyRenderer(self.uuid)
        self.uuid = b''

    def __del__(self):
        self.destroy()
