from functools import partial
from collections import OrderedDict
from .Qt import QtWidgets, QtCore
from .arg import Arg
from .string import String, Info
from .text import Doc, Python, Mel
from .array import Array
from .number import Float, Integer
from .item import Item
from .boolean import Boolean
from .path import Path

TYPES = {
        'object': Arg,
        'info': Info,
        'string': String,
        'doc': Doc,
        'path': Path,
        'mel': Mel,
        'python': Python,
        'array': Array,
        'item': Item,
        'boolean': Boolean,
        'float': Float,
        'integer': Integer
}

def deleteChildWidgets(item):
    layout = item.layout()
    if layout:
        for i in range(layout.count()):
            deleteChildWidgets(layout.itemAt(i))
    if item.widget():
        item.widget().deleteLater()

def get_object_from_type(type):
    return TYPES[type]

class ResetButton(QtWidgets.QPushButton):
    def __init__(self, wdg, label = '<', *args, **kwargs):
        super(ResetButton, self).__init__(label, *args, **kwargs)
        self.wdg = wdg

    def paintEvent(self, event):
        super(ResetButton, self).paintEvent(event)
        self.setFixedSize(35, self.wdg.sizeHint().height())

class ArgParser(QtWidgets.QWidget):
    changed = QtCore.Signal()

    def __init__(self, 
                 data=None,
                 label_suffix=None,
                 description='',
                 parent=None):

        #Init
        self._description = description
        self._label_suffix = label_suffix
        self._args = OrderedDict()

        super(ArgParser, self).__init__(parent)

        #Layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setRowStretch(999, 1)
        layout.setVerticalSpacing(2)
        layout.setColumnStretch(0, 0)

        # Construct from data
        if data:
            for name in data:
                _data = data[name]
                _data['name'] = name
                self.add_arg(**_data)

        self._write = lambda *args, **kwargs: (self._args[name]._write(*args, **kwargs) \
                                               for name in self._args)
        self._read = lambda : {self._args[name].name : self._args[name]._read() \
                               for name in self._args.keys()}

    def __repr__(self):
        return '%s(%s)' %(self.__class__.__name__, 
                          dict(self._args))

    @property
    def _row(self):
        return len(self._args)

    def add_arg(self, 
                name=None, 
                type=None, 
                default=None, 
                **kwargs):

        arg = get_object_from_type(type)(name, 
                                         default,
                                         **kwargs)

        self._add_arg(arg)
        return arg

    def _add_arg(self, arg):
        name = arg._data["name"]
        if name in self._args:
            raise ValueError("Duplicate argument '%s'" %name)

        #Create widget
        wdg = arg.create()
        desc = arg._data.get('description')
        wdg.setToolTip(desc)

        #Reset
        reset_button = ResetButton(wdg)
        reset_button.clicked.connect(arg.reset)
        arg.changed.connect(partial(self.on_changed, arg, reset_button))
        reset_button.hide()

        #add widget to Layout
        layout = self.layout()
        label = arg._data['label']

        if self._label_suffix:
            label = "%s%s "%(label, self._label_suffix)

        layout.addWidget(QtWidgets.QLabel(label), 
                         self._row, 0, 
                         QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        layout.addWidget(wdg, 
                         self._row, 1, 
                         QtCore.Qt.AlignTop)
        layout.addWidget(reset_button, 
                         self._row, 2, 
                         QtCore.Qt.AlignTop)     
                         
        self._args[name] = arg

    def delete_arg(self, name, wdg):
        layout = self.layout()

        #Delete layout row
        row = None
        for i in range(layout.count() - 1):
            r, c, rs, cs = layout.getItemPosition(i)
            item = layout.itemAt(i)
            if item.widget() is wdg:
                row = r
                break
        else:
            raise RuntimeError('Row not found')

        for col in range(layout.columnCount()):
            item = layout.itemAtPosition(row, col)
            deleteChildWidgets(item)
            layout.removeItem(item)

        layout.setRowMinimumHeight(row, 0)
        layout.setRowStretch(row, 0)

        self._args.pop(name)

    def delete_children(self):
        layout = self.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item :
                deleteChildWidgets(item)
        self._args = OrderedDict()

    def on_changed(self, arg, button, *args, **kwargs):
        button.setVisible(arg.is_edited())
        self.changed.emit()

    def export_data(self):
        return self._read()