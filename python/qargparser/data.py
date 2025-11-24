
from . import utils


class ArgparserData:
    def __init__(self, data=None):
        self.data = data

    def __iter__(self):
        return iter(self.data)
        
    @classmethod
    def from_path(cls, path):
        data = utils.read_json(path)
        return cls(data)
    
    def to_values(self):
        return {
            arg["name"]: arg["default"] for arg in self.data
        }