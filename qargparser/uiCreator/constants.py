import os

import qargparser
from ..constants import EXT 

_root = os.path.dirname(__file__)
PROPERTIES_PATH = os.path.join(_root, "properties")
BASE_PROPERTIES_FILE = os.path.join(PROPERTIES_PATH, "base.json")
PROPERTIES_MAPPING_NAMES = {
    "int": "integer",
    "bool": 'boolean',
    "info": 'string',
    "python": 'text',
    "mel": 'text', 
    "doc": 'text', 
    "python": 'text'
}     


#UI
NAME_IDX = 0
TYPE_IDX = 1
ADD_IDX = 1

WIN_WIDTH = 2500
WIN_HEIGHT = 1800

READPREVIEW_WIN_WIDTH = 1500
READPREVIEW_WIN_HEIGHT = 1500

SPLITTER_RATIOS = [0.2, 0.5, 0.3]

#Style
STYLE_FILE = os.path.join(_root, "style", 'style.css')
STYLEVARS_FILE = os.path.join(_root, "style", 'styleVars.json')
ICONS_PATH = os.path.join(_root, "style", "icons").replace("\\", "/")

EXAMPLES_DIR_PATH = os.path.join(_root, "examples")
EXAMPLES_NAMES = ["allArgClasses"]