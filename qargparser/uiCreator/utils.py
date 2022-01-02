import os
import json
import re
import json
from ..utils import load_data_from_file, write_json
from . import constants as cons

def get_properties_data(name):
    #Get true file name
    name = cons.PROPERTIES_MAPPING_NAMES.get(name, name)
    #Get base data
    data = load_data_from_file(cons.BASE_PROPERTIES_FILE)
    #Update data
    path = os.path.join(cons.PROPERTIES_PATH, name+".json")
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

def load_style():
    #Get style string
    vars_dct = load_data_from_file(cons.STYLEVARS_FILE)
    with open(cons.STYLE_FILE, "r") as f:
        string = f.read()

    #Replaceskeys by vars values
    for name in vars_dct.keys():
        string = string.replace('<'+str(name)+'>', vars_dct[name])

    #Replace icons path keys by valyes
    string = string.replace('<path>', cons.ICONS_PATH)
    return string
