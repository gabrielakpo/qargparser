import os

from . import utils, envs
from .decorators import SingletonDecorator


@SingletonDecorator
class PropertiesManager(object):
    def __init__(self):
        self._data = {}

        for file_name in os.listdir(envs.PROPERTIES_PATH):
            name, ext = os.path.splitext(file_name)

            if ext != envs.FILE_EXT:
                continue

            file_path = os.path.join(envs.PROPERTIES_PATH, file_name)
            self._data[name] = utils.read_json(file_path)

    def get_data(self, type, default=False):
        data = self._data[envs.PROPERTIES_BASE_NAME][:]

        name = envs.PROPERTIES_MAPPING_NAMES.get(type, type)
        file_path = os.path.join(envs.PROPERTIES_PATH, name+envs.FILE_EXT)

        if os.path.isfile(file_path):
            data.extend(utils.read_json(file_path))
        else:
            print("Could not find property for {}".format(name))

        if default:
            data = {d["name"]: d["default"] for d in data}
            data["type"] = name
            data["name"] = data["type"]

        return data