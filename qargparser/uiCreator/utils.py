import os
import json
import re
import json
from .. import utils as qargp_utils

ROOT = os.path.dirname(__file__)
PROPERTIES_PATH = os.path.join(ROOT, "properties")

def get_base_properties():
    return qargp_utils.load_data_from_file(os.path.join(PROPERTIES_PATH, "base.json"))
    
def get_properties(name):
    bases = get_base_properties()

    name = {"int": "integer",
            "bool": 'boolean',
            "info": 'string',
            "python": 'text',
            "mel": 'text', 
            "doc": 'text', 
            "python": 'text'}.get(name, name)

    path = os.path.join(PROPERTIES_PATH, name+".json")
    if os.path.isfile(path):
        data = qargp_utils.load_data_from_file(path) or {}
        bases.extend(data)
    return bases

def write_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

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


def load_style():
    d = os.path.join(os.path.dirname(__file__), "style")
    style_path = os.path.join(d, 'style.css')
    vars_path = os.path.join(d, 'styleVars.json')

    vars_dct = qargp_utils.load_data_from_file(vars_path)
    with open(style_path,"r") as f:
        string = f.read()

    for name in vars_dct.keys():
        string=string.replace('<'+str(name)+'>', vars_dct[name])

    string = string.replace('<path>', os.path.join(d, "icons").replace("\\", "/"))
    return string

def clear_layout(layout):
    """Delete all UI children recurcively

    :param layout: layout parent, defaults to None
    :type layout: QLayout, optional
    """
    while layout.count():
        item = layout.takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            lay = item.layout()
            if lay:
                clear_layout(lay) 