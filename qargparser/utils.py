import json
from collections import OrderedDict as BaseOrderedDict, Mapping

class OrderedDict(BaseOrderedDict):
    def insert(self, idx, key, value):
        size = len(self.keys())
        if key in self.keys():
            size -= 1
            
        if idx == -1 or idx > size:
            idx = size
        self[key] = value
        
        while(self.items()[idx][0] != key):
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
    with open(path, 'r') as f:
        data = json.load(f,  object_pairs_hook=OrderedDict)
        return data

def to_dict(o_dict):
    return json.loads(json.dumps(o_dict)) 

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