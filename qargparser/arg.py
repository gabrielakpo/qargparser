from .Qt import QtWidgets, QtCore
import re

def to_label_string(text):
    return re.sub(
        r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))",
        r" \1", text
    ).title()

class Arg(QtCore.QObject):
    default = None
    changed = QtCore.Signal(tuple)
    
    def __init__(self, name, default=None, **kwargs):
        super(Arg, self).__init__(kwargs.pop('parent', None))
        
        kwargs['name'] = name
        kwargs['label'] = kwargs.get('label') or to_label_string(name)
        kwargs['default'] = default or self.default
        kwargs['description'] = kwargs.get('description', '')

        self._data = kwargs
        self._write = None
        self._read = None

    def __repr__(self):
        return '%s(%s)' %(self.__class__.__name__, 
                          dict(self._data))

    def create(self):
        if self._data.get('items'):

            from .argparser import ArgParser

            wdg = ArgParser(description=self._data['description'])
            data = self._data.get('items')

            for name in data:
                _data = data[name]
                _data['name'] = name
                wdg.add_argument(**_data)
        else:
            wdg = QtWidgets.QWidget()

        return wdg

    def delete(self):
        pass

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
