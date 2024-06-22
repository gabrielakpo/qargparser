# Icons
import os
_root = os.path.dirname(__file__)

DOC_FILE = os.path.join(os.path.abspath(
    os.path.join(_root, "..")), "docs", "index.html")

FILE_EXT = ".json"

# Reload button
RELOAD_ICON = os.path.join(_root, "icons", "reload.png")
RELOAD_BUTTON_WIDTH = 15
RELOAD_BUTTON_MIN_HEIGHT = 20
RELOAD_BUTTON_ICON_SIZE = 10

# Item delete button
ITEM_DEL_BUTTON_WIDTH = 15
ITEM_DEL_BUTTON_MIN_HEIGHT = 20

NAMES_ORDER = [
    "name",
    "type",
    "description",
    "min",
    "max",
    "step",
    "slider",
    "buttonLabel",
    "searchMessage",
    "enums",
    "enumsDescriptions",
    "default",
    "items"]

DEFAULT_DATA = {
    "array": {
        "default": [],
        "min": 0,
        "max": 10000,
        "buttonLabel": "Add Item",
        "items": {},
    },
    "integer": {
        "default": 0,
        "step": 1,
        "min": -10000,
        "max": 10000,
        "slider": False
    },
    "float": {
        "default": 0.0,
        "step": 0.1,
        "min": -10000.0,
        "max": 10000.0,
        "slider": False
    },
    "object": {
        "default": {},
        "items": [],
    },
    "tab": {
        "default": {},
        "movable": True,
        "closable": False,
        "items": [],
    },
    "path": {
        "default": "",
        "buttonLabel": "...",
        "searchMessage": "Choose a path",
        "filters": "",
        "mode": "all",
    },
    "enum": {
        "default": "",
        "enums": [],
        "enumsDescriptions": []
    },
    "text": {
        "default": ""
    },
    "doc": {
        "default": ""
    },
    "code": {
        "default": ""
    },
    "python": {
        "default": "#Python"
    },
    "mel": {
        "default": "//Mel"
    },
    "boolean": {
        "default": False
    },
    "item": {
        "default": None,
        "template": {}
    },
    "string": {
        "default": "",
        "placeHolder": "",
    },
    "info": {
        "default": ""
    },
    "color": {
        "default": [0.0, 0.0, 0.0],
        "slider": True,
        "spinbox": True,
        "alpha": False
    },
    "dict": {
        "default": {},
        "max": 10000,
        "min": 0,
        "buttonLabel": "Add Item",
        "readOnly": False,
        "items": {}
    }
}

IDX_COLORS = [
    [0.0, 0.0, 0.0],
    [0.25, 0.25, 0.25],
    [0.6000000238418579, 0.6000000238418579, 0.6000000238418579],
    [0.6079999804496765, 0.0, 0.15700000524520874],
    [0.0, 0.01600000075995922, 0.37599998712539673],
    [0.0, 0.0, 1.0],
    [0.0, 0.2750000059604645, 0.09799999743700027],
    [0.14900000393390656, 0.0, 0.2630000114440918],
    [0.7839999794960022, 0.0, 0.7839999794960022],
    [0.5410000085830688, 0.28200000524520874, 0.20000000298023224],
    [0.24699999392032623, 0.13699999451637268, 0.12200000137090683],
    [0.6000000238418579, 0.14900000393390656, 0.0], [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.2549999952316284, 0.6000000238418579],
    [1.0, 1.0, 1.0],
    [1.0, 1.0, 0.0],
    [0.3919999897480011, 0.8629999756813049, 1.0],
    [0.2630000114440918, 1.0, 0.6389999985694885],
    [1.0, 0.6899999976158142, 0.6899999976158142],
    [0.8939999938011169, 0.675000011920929, 0.4749999940395355],
    [1.0, 1.0, 0.3880000114440918],
    [0.0, 0.6000000238418579, 0.32899999618530273],
    [0.6299999952316284, 0.41391000151634216, 0.1889999955892563],
    [0.62117999792099, 0.6299999952316284, 0.1889999955892563],
    [0.40950000286102295, 0.6299999952316284, 0.1889999955892563],
    [0.1889999955892563, 0.6299999952316284, 0.3653999865055084],
    [0.1889999955892563, 0.6299999952316284, 0.6299999952316284],
    [0.1889999955892563, 0.4050999879837036, 0.6299999952316284],
    [0.43595999479293823, 0.1889999955892563, 0.6299999952316284],
    [0.6299999952316284, 0.1889999955892563, 0.41391000151634216]]
