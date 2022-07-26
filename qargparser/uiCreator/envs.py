import os

from ..envs import EXT 

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

READPREVIEW_WIN_WIDTH = 750
READPREVIEW_WIN_HEIGHT = 750

SPLITTER_RATIOS = [0.25, 0.5, 0.25]

#Style
STYLE_ROOT = os.path.join(_root, "style").replace('\\', '/')
STYLE_FILE = os.path.join(STYLE_ROOT, 'style.qss')
STYLEVARS_FILE = os.path.join(STYLE_ROOT, 'styleVars.json')
ICONS_PATH = os.path.join(STYLE_ROOT, "icons").replace("\\", "/")

EXAMPLES_DIR_PATH = os.path.join(_root, "examples")
EXAMPLES_NAMES = ["allArgClasses"]