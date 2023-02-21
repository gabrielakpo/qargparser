import os

from ..envs import EXT 
from .Qt import QtGui

_root = os.path.dirname(__file__)
PROPERTIES_PATH = os.path.join(_root, "properties")
BASE_PROPERTIES_FILE = os.path.join(PROPERTIES_PATH, "base.json")
PROPERTIES_MAPPING_NAMES = {
    "int": "integer",
    "bool": 'boolean',
    "python": 'text',
    "mel": 'text', 
    "doc": 'text', 
    "python": 'text'
}     


#UI
NAME_IDX = 0
TYPE_IDX = 1
ADD_IDX = 1

WIN_WIDTH = 1000
WIN_HEIGHT = 700

PREVIEW_WIN_WIDTH = 750
PREVIEW_WIN_HEIGHT = 750

SPLITTER_RATIOS = [0.25, 0.5, 0.25]

#Style
STYLE_ROOT = os.path.join(_root, "style").replace('\\', '/')
STYLE_FILE = os.path.join(STYLE_ROOT, 'style.qss')
STYLEVARS_FILE = os.path.join(STYLE_ROOT, 'styleVars.json')
ICONS_PATH = os.path.join(STYLE_ROOT, "icons").replace("\\", "/")

EXAMPLES_DIR_PATH = os.path.join(_root, "examples")
EXAMPLES_NAMES = ["allArgClasses"]

CURRENT_AP = None


class DirFiles(dict):
    def __init__(self, root, *args, **kwargs):
        self._root = root
        super(DirFiles, self).__init__(*args, **kwargs)
        
    def __getitem__(self, __k):
        if __k in self:
            return os.path.join(self._root, 
                                super(DirFiles, self).__getitem__(__k))

    def get(self, __k, default=None):
        if __k in self:
            return self.__getitem__(__k)
        return default

class CacheIcons(dict):
    def __getitem__(self, __k):
        if not __k:
            return QtGui.QIcon()

        if __k not in self:
            if not os.path.isfile(__k):
                super(CacheIcons, self).__setitem__(__k, QtGui.QIcon(IMAGES[__k]))
            else:
                super(CacheIcons, self).__setitem__(__k, QtGui.QIcon(__k))
                
        return super(CacheIcons, self).__getitem__(__k)

IMAGES = DirFiles(os.path.join(_root, "icons"), {
    "read_preview": "read_preview.png",

    "valid": "valid.png",
    "reset": "reset.png",
    "move_up": "move_up.png",
    "move_down": "move_down.png",
    "delete": "delete.png",
    "clear": "clear.png",

    "type_array": "type_array.png",
    "type_boolean": "type_boolean.png",
    "type_code": "type_code.png",
    "type_color": "type_color.png",
    "type_dict": "type_dict.png",
    "type_doc": "type_doc.png",
    "type_enum": "type_enum.png",
    "type_float": "type_float.png",
    "type_info": "type_info.png",
    "type_integer": "type_integer.png",
    "type_mel": "type_mel.png",
    "type_object": "type_object.png",
    "type_path": "type_path.png",
    "type_python": "type_python.png",
    "type_string": "type_string.png",
    "type_text": "type_text.png",
    "type_tab": "type_tab.png"
})

ICONS = CacheIcons()