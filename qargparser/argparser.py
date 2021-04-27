from functools import partial
from collections import OrderedDict
from .Qt import QtWidgets, QtCore
from .arg import Arg
from .string import String
from .code import Python, Mel
from .array import Array
from .number import Float, Integer
from .item import Item
from .boolean import Boolean
from .path import Path

def deleteChildWidgets(item):
    layout = item.layout()
    if layout:
        for i in range(layout.count()):
            deleteChildWidgets(layout.itemAt(i))
    if item.widget():
        item.widget().deleteLater()

def get_object_from_type(type):
    types = {
        'object': Arg,
        'string': String,
        'path': Path,
        'mel': Mel,
        'python': Python,
        'array': Array,
        'item': Item,
        'boolean': Boolean,
        'float': Float,
        'interger': Integer
    }
    return types[type]

class ResetButton(QtWidgets.QPushButton):
    def __init__(self, wdg, label = '<', *args, **kwargs):
        super(ResetButton, self).__init__(label, *args, **kwargs)
        self.wdg = wdg

    def paintEvent(self, event):
        super(ResetButton, self).paintEvent(event)
        self.setFixedSize(35,
                                   self.wdg.sizeHint().height())

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
        self._arguments = OrderedDict()

        super(ArgParser, self).__init__(parent)

        #Layout
        layout = QtWidgets.QGridLayout(self)
        layout.setRowStretch(999, 1)
        layout.setVerticalSpacing(2)

        # Construct from data
        if data:
            for name in data:
                _data = data[name]
                _data['name'] = name
                self.add_argument(**_data)


    def __repr__(self):
        return '%s(%s)' %(self.__class__.__name__, 
                          dict(self._arguments))

    @property
    def _row(self):
        return len(self._arguments)

    def add_argument(self, 
                    name=None, 
                    type=None, 
                    default=None, 
                    **kwargs):

        argument = get_object_from_type(type)(name, 
                                            default,
                                            **kwargs)

        self._add_argument(argument)
        return argument

    def _add_argument(self, argument):
        name = argument._data["name"]
        if name in self._arguments:
            raise ValueError("Duplicate argument '%s'" %name)

        #Create widget
        wdg = argument.create()
        desc = argument._data.get('description')
        wdg.setToolTip(desc)

        #Reset
        reset_button = ResetButton(wdg)
        reset_button.clicked.connect(argument.reset)
        argument.changed.connect(partial(self.on_changed, argument, reset_button))
        reset_button.hide()

        #add widget to Layout
        layout = self.layout()
        label = argument._data['label']
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
                         
        self._arguments[name] = argument

    def delete_argument(self, name, wdg):
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

        self._arguments.pop(name)

    def delete_children(self):
        layout = self.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item :
                deleteChildWidgets(item)
        self._arguments = OrderedDict()

    def on_changed(self, arg, button):
        button.setVisible(arg.is_edited())
        self.changed.emit()

    def export_data(self):
        data = OrderedDict()
        for name, arg in self._arguments.items():
            data[name] = arg.read()
        return data