from .object import Object
from .string import String, Info
from .text import Text, Doc, Python, Mel, Code
from .array import Array
from .number import Float, Integer
from .boolean import Boolean
from .path import Path
from .color import Color
from .dict import Dict
from .tab import Tab
from .enum import Enum

TYPES = {
    "object": Object,
    "tab": Tab,
    "enum": Enum,
    "info": Info,
    "string": String,
    "text": Text,
    "doc": Doc,
    "dict": Dict,
    "path": Path,
    "code": Code,
    "mel": Mel,
    "python": Python,
    "array": Array,
    "boolean": Boolean,
    "float": Float,
    "integer": Integer,
    "color": Color,
}
