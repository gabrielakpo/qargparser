import json
import os
from collections import OrderedDict as BaseOrderedDict
import sys

if sys.version_info[0] == 3:
    from collections.abc import Mapping
else:
    from collections import Mapping


class OrderedDict(BaseOrderedDict):
    def insert(self, idx, key, value):
        size = len(self.keys())
        if key in self.keys():
            size -= 1

        if idx == -1 or idx > size:
            idx = size
        self[key] = value

        while (self.items()[idx][0] != key):
            k = self.items()[0][0]
            v = self.pop(k)
            self[k] = v


def clean_unicodes(data):
    _dct = type(data)()
    for k, v in list(data.items()):
        if isinstance(v, Mapping):
            _dct[str(k)] = clean_unicodes(v)
        else:
            if isinstance(v, unicode):
                v = str(v)
            _dct[str(k)] = v
    return _dct


def load_data_from_file(path):
    return read_json(path, object_pairs_hook=OrderedDict)


def to_dict(o_dict):
    return json.loads(json.dumps(o_dict))


def read_json(path, **kwargs):
    with open(path, 'r') as f:
        data = json.load(f,  **kwargs)
        return data


def write_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


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


def pretty_description(txt, next_line=80):
    punctuation = "!)}, .:;?"
    new = []
    counter = 0
    for c in txt:
        new.append(c)
        if counter > next_line and c in punctuation:
            new.append("\n")
            counter = 0
        counter += 1
    return "".join(new)


def make_dir(path):
    """Create a new directory if it doesn't exist

    :param path: path of the directory
    :type path: str
    :return: path of the created directory
    :rtype: str
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            pass

    return os.path.exists(path)
