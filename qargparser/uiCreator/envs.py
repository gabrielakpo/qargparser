import os

from qargparser.envs import FILE_EXT, DOC_FILE
from .Qt import QtGui

_root = os.path.dirname(__file__)
PROPERTIES_PATH = os.path.join(_root, "properties")
BASE_PROPERTIES_FILE = os.path.join(PROPERTIES_PATH, "base.json")
PROPERTIES_MAPPING_NAMES = {
    "int": "integer",
    "bool": 'boolean',
    "python": 'text',
    "mel": 'text',
    "doc": 'text'
}

FILE_FILTERS = "JSON (**.json)"

# UI
NAME_IDX = 0
TYPE_IDX = 1
ADD_IDX = 1

WIN_WIDTH = 1000
WIN_HEIGHT = 700

PREVIEW_WIN_WIDTH = 750
PREVIEW_WIN_HEIGHT = 750

SPLITTER_RATIOS = [0.25, 0.5, 0.25]

# theme
THEME_ROOT = os.path.join(_root, "styles").replace('\\', '/')
THEME_EXTS = [".qss", ".css"]

EXAMPLES_DIR_PATH = os.path.join(_root, "examples")

CURRENT_AP = None

# preferences
THEME_KEY = "theme"

PREFS_DEFAULT = {
    THEME_KEY: "default"
}

PREFS_ROOT_NAME = ".qargparser"
PREFS_FILE_NAME = "qargparser_prefs.json"

# settings
SETTINGS_FILE_NAME = "qarparser_settings.ini"


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
                super(CacheIcons, self).__setitem__(__k, QtGui.QIcon(FILES[__k]))
            else:
                super(CacheIcons, self).__setitem__(__k, QtGui.QIcon(__k))

        return super(CacheIcons, self).__getitem__(__k)


FILES = DirFiles(os.path.join(_root, "icons"), {
    "app": "app.png",
    "throbber": "throbber.png",
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