from .Qt import QtCore
from . import utils
from . import constants as cons

class ArgData(dict):

    def __init__(self, *args, **kwargs):
        super(ArgData, self).__init__(*args, **kwargs)
        ref = args[0]
        if ref["type"] in cons.DEFAULT_DATA:
            for key in cons.DEFAULT_DATA[ref["type"]]:
                if not key in self or self[key] is None:
                    super(ArgData, self).__setitem__(key, cons.DEFAULT_DATA[ref["type"]][key])

    def __repr__(self):
        return "<%s %s>"%(self.__class__.__name__, super(ArgData, self).__repr__())

class Arg(QtCore.QObject):
    changed = QtCore.Signal(tuple)
    reset_requested = QtCore.Signal()
    
    def __init__(self, name=None, default=None, **kwargs):
        super(Arg, self).__init__(kwargs.pop('parent', None))

        kwargs['name'] = name
        kwargs['type'] = self.__class__.__name__.lower()
        kwargs['default'] = default
        kwargs['description'] = kwargs.get('description', "")

        self.wdg = None
        self._data = ArgData(kwargs)
        self._write = None
        self._read = None

    @property
    def name(self):
        return self._data['name']  

    def __repr__(self):
        return '<%s( %s )>' %(self.__class__.__name__, 
                          self._data.items())

    def __call__(self, key, default=None):
        return self._data.get(key, default)

    def create(self):
        pass
        
    def set_data(self, name, value):
        self._data[name] = value
        self._update()

    def update_data(self, data):
        self._data.update(data)
        self._update()

    def _update(self):
        desc = self._data['description']
        if desc.strip():
            self.wdg.setToolTip(desc)
        self.reset()

    def delete(self):
        utils.clear_layout(self.wdg.layout())
        self.wdg.deleteLater()

    def get_children(self):
        return []

    def write(self, value):
        return self._write(value)

    def read(self):
        return self._read()

    def reset(self):
        self.changed.emit(None)

    def is_edited(self):
        return self.read() != self._data["default"]

    def on_changed(self, *args):
        if not args:
            args = (None, )
        self.changed.emit(*args)

    def to_data(self):
        data = utils.OrderedDict(
            sorted([item for item in self._data.items() if item[1] is not None], 
                   key=lambda x: cons.NAMES_ORDER.index(x[0]) 
                                 if x[0] in cons.NAMES_ORDER else 0))
        return data
