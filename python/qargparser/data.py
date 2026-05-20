
from copy import deepcopy

from . import utils


class ArgparserData:
    def __init__(self, data=None):
        self.data = data or []

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

    def copy(self):
        """Return a deep copy of this ArgparserData."""
        return ArgparserData(deepcopy(self.data))

    def set_default(self, name, default, inplace=True):
        """Update the default value of a given argument by name.

        If inplace is True, modifies this instance and returns self.
        If inplace is False, returns a new ArgparserData instance with the
        updated default and leaves the original untouched.
        """
        target = self.data if inplace else deepcopy(self.data)

        for arg in target:
            if "name" in arg and arg["name"] == name:
                arg["default"] = default
                break
        else:
            raise KeyError(f"Argument with name '{name}' not found in ArgparserData")

        if inplace:
            return self
        return ArgparserData(target)