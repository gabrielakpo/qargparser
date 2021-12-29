from .Qt import QtCore
from . import utils

def clear_layout(layout):
    """Delete all UI children recurcively

    :param layout: layout parent, defaults to None
    :type layout: QLayout, optional
    """
    if not layout:
        return 

    while layout.count():
        item = layout.takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            lay = item.layout()
            if lay:
                clear_layout(lay) 

class Arg(QtCore.QObject):
    default = None
    changed = QtCore.Signal(tuple)
    deleted = QtCore.Signal()
    
    def __init__(self, name, default=None, **kwargs):
        super(Arg, self).__init__(kwargs.pop('parent', None))
        
        kwargs['name'] = name
        kwargs['type'] = self.__class__.__name__.lower()
        kwargs['default'] = default or self.default
        kwargs['description'] = kwargs.get('description', '')

        self.wdg = None
        self._data = kwargs
        self._write = None
        self._read = None

    @property
    def name(self):
        return self._data['name'] 

    def __repr__(self):
        import pprint
        return '<\n\n[%s]\n%s>' %(self.__class__.__name__, 
                          pprint.pformat(utils.clean_unicodes(utils.to_dict(self._data))))

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
        self.label_ui.setText(self._data["name"])
        desc = self._data.get('description')
        if desc.strip():
            self.wdg.setToolTip(desc)
        self.reset()

    def delete(self):
        clear_layout(self.wdg.layout())
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
        data = self._data.copy()
        return data
