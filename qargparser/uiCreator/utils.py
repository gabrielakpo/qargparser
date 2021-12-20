import os
from qargparser import utils as qargp_utils

ROOT = os.path.dirname(__file__)
PROPERTIES_PATH = os.path.join(ROOT, "properties")

def get_base_properties():
    return qargp_utils.load_data_from_file(os.path.join(PROPERTIES_PATH, "base.json"))
    
def get_properties(name):
    bases = get_base_properties()
    data = qargp_utils.load_data_from_file(os.path.join(PROPERTIES_PATH, name+".json")) or {}
    bases.update(data)
    return bases
