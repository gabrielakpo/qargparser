import json
from collections import OrderedDict

def load_data_from_file(path):
    with open(path, 'r') as f:
        data = json.load(f,  object_pairs_hook=OrderedDict)
        return data