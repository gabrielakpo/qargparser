import os
import json
import re
import json
from ..utils import load_data_from_file, write_json
from .Qt import QtWidgets
from . import envs 

def get_properties_data(name):
    #Get true file name
    name = envs.PROPERTIES_MAPPING_NAMES.get(name, name)
    #Get base data
    data = load_data_from_file(envs.BASE_PROPERTIES_FILE)
    #Update data
    path = os.path.join(envs.PROPERTIES_PATH, name+".json")
    if os.path.isfile(path):
        data.extend(load_data_from_file(path) or {})

    return data

def format_json(data, indent=4):
    return json.dumps(data, indent=indent)

def split_digits(string):
    match = re.match('.*?([0-9]+)$', string)
    if match is not None:
        split = [string.rpartition(match.group(1))[0], match.group(1)]
    else:
        split = [string, None]
    return split

def get_next_name(string):
    n, idx = split_digits(string)
    if not idx:
        idx = "0"
    idx = str(int(idx) + 1)
    return  n + idx

def _load_style():
    path = envs.STYLE_FILE
    with open(path, "r") as f:
        data = f.read()
        data = data.replace('<rootpath>', envs.STYLE_ROOT)
    return _scaled_stylesheet(data)

def _px(value):
    #Get screen resolution
    rec = QtWidgets.QApplication.desktop().screenGeometry()
    h = rec.height()
    factor = h / 2160.0
    return factor * value

def _scaled_stylesheet(ss):
    """Replace any mention of <num>px with scaled version
    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.
    """

    output = []
    for line in ss.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            key, value = line.rsplit(" ", 1)
            try:
                value = _px(int(value[:-3]))
                line = "%s %dpx;" % (key, value)
            except:
                pass
        output += [line]
    return "\n".join(output)

def get_example_path(name):
    dir_path = envs.EXAMPLES_DIR_PATH
    path = os.path.join(dir_path, name+envs.EXT)
    return path
