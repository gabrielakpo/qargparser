import os
import json
import re

from qargparser.utils import (
    load_data_from_file,
    read_json,
    write_json)

from . import envs


def get_properties_data(name, default=False):
    #Get true file name
    name = envs.PROPERTIES_MAPPING_NAMES.get(name, name)
    #Get base data
    data = load_data_from_file(envs.BASE_PROPERTIES_FILE)
    #Update data
    path = os.path.join(envs.PROPERTIES_PATH, name+".json")
    if os.path.isfile(path):
        data.extend(load_data_from_file(path) or {})

    if default:
        data = {d["name"]: d["default"] for d in data}
    return data


def make_dir(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            pass
    return os.path.exists(path)


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


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


def get_example_path(name):
    dir_path = envs.EXAMPLES_DIR_PATH
    path = os.path.join(dir_path, name+envs.FILE_EXT)
    return path


def get_example_names():
    names = []
    for name in os.listdir(envs.EXAMPLES_DIR_PATH):
        base, ext = os.path.splitext(name)
        if ext == envs.FILE_EXT:
            names.append(base)
    return names


def show_documentation():
    """Opens documentation file in browser
    """
    if not os.path.isfile(envs.DOC_FILE):
        raise RuntimeError("Could not find doumentation.")

    import webbrowser
    webbrowser.open(os.path.join('file:', envs.DOC_FILE))