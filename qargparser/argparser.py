from functools import partial
from collections import OrderedDict
from .Qt import QtWidgets, QtCore, QtGui
from .object import Object
from .string import String, Info
from .text import Text, Doc, Python, Mel
from .array import Array, ArrayObject
from .number import Float, Integer
from .item import Item, ItemObject
from .boolean import Boolean
from .path import Path
from .enum import Enum
from . import utils
from . import constants as cons
import re

TYPES = {
    'object': Object,
    'enum': Enum,
    'info': Info,
    'string': String,
    'text': Text,
    'doc': Doc,
    'path': Path,
    'mel': Mel,
    'python': Python,
    'array': Array,
    'arrayobject': ArrayObject,
    'item': Item,
    'itemobject': ItemObject,
    'boolean': Boolean,
    'float': Float,
    'integer': Integer,
}

_TYPES = TYPES.copy()
_TYPES.update({
    'bool': Boolean,
    'int': Integer
})

def deleteChildWidgets(item):
    layout = item.layout()
    if layout:
        for i in range(layout.count()):
            deleteChildWidgets(layout.itemAt(i))
    if item.widget():
        item.widget().deleteLater()

def get_object_from_type(type):
    return _TYPES[type]

class ResetButton(QtWidgets.QPushButton):
    def __init__(self, wdg, label = '*', *args, **kwargs):
        super(ResetButton, self).__init__(QtGui.QIcon(cons.RELOAD_ICON), 
                                          "", 
                                          *args, **kwargs)
        self.setIconSize(QtCore.QSize(25, 25))
        self.wdg = wdg

    def paintEvent(self, event):
        super(ResetButton, self).paintEvent(event)
        height = self.wdg.sizeHint().height()
        if height < 35:
            height = 35
        self.setFixedSize(35, height)

def to_label_string(text):
    if text is None:
        text = ""
    return re.sub(
        r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))",
        r" \1", text
    ).title()

class CustomLabel(QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        self.label_suffix = kwargs.pop("label_suffix", None)
        if args:  
            args = [self._new_text(args[0])] + [e for e in args[1:]]

        super(CustomLabel, self).__init__(*args, **kwargs)

        self.setMaximumWidth([0, 1000][bool(args[0])])
            
    def setText(self, txt):
        txt = self._new_text(txt)
        self.setMaximumWidth([0, 1000][bool(txt)])
        super(CustomLabel, self).setText(txt)

    def _new_text(self, txt):
        txt = to_label_string(txt)
        if self.label_suffix:
            txt = "%s%s "%(txt, self.label_suffix)
        return txt

class ArgParser(QtWidgets.QGroupBox):
    changed = QtCore.Signal()

    def __init__(self, 
                 data=None,
                 label_suffix=None,
                 description='',
                 parent=None):

        #Init
        self._nb_deleted = 0
        self._description = description
        self._label_suffix = label_suffix
        self._args = []

        super(ArgParser, self).__init__(parent)

        #Layout
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setFormAlignment(QtCore.Qt.AlignTop)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setVerticalSpacing(5)

        # build from data
        if data:
            self.build(data)

        self._write = lambda *args, **kwargs: (arg._write(*args, **kwargs) for arg in self._args)
        self._read = lambda : OrderedDict((arg("name"), arg._read()) for arg in self._args)

    def __repr__(self):
        return '<%s( %s )>' %(self.__class__.__name__, 
                              self._args)

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
        # name = arg._data["name"]
        # if self.get_arg(name):
        #     raise ValueError("Duplicate argument '%s'" %name)

        #Create widget
        wdg = arg.create()
        desc = arg._data.get('description')
        if desc.strip():
            wdg.setToolTip(desc)

        #Reset
        reset_button = ResetButton(wdg)
        reset_button.clicked.connect(arg.reset)
        arg.changed.connect(partial(self.on_changed, arg, reset_button))
        reset_button.hide()

        #add widget to Layout
        layout = self.layout()
        label = arg._data['name']

        label_ui = CustomLabel(label, label_suffix=self._label_suffix)

        row_wdg = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row_wdg)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        row_layout.addWidget(reset_button)
        row_layout.addWidget(wdg)
        
        layout.insertRow(self._row,
                        label_ui, 
                        row_wdg)
                         
        self._args.append(arg)

    def get_arg(self, key):
        for i, arg in enumerate(self._args):
            if ((isinstance(key, int) and i == key) 
            or (isinstance(key, str) and arg("name") == key)):
                return arg

    def pop_arg(self, arg):
        layout = self.layout()
        idx, _ = layout.getWidgetPosition(arg.wdg.parent())

        #Label
        lay_item = layout.itemAt(idx, QtWidgets.QFormLayout.LabelRole)
        deleteChildWidgets(lay_item)
        layout.removeItem(lay_item)

        #widget
        lay_item = layout.itemAt(idx, QtWidgets.QFormLayout.FieldRole)
        deleteChildWidgets(lay_item)
        layout.removeItem(lay_item) 

        self._args.remove(arg)

    def move_arg(self, key, idx):
        if isinstance(key, int):
            key = self._args[key]

        label = self.get_label(key)
        label.setParent(None)

        wdg = self.get_widget()
        wdg.setParent(None)

        self._args.remove(key)
        self._args.insert(idx, key)

        layout = self.layout()

        _idx = 0
        if idx > 0:
            if idx >= len(self._args) - 1:
                _idx = layout.rowCount()
            else:
                _idx = layout.getWidgetPosition(self._args[idx+1].wdg.parent())[0] - 1

        layout.insertRow(_idx+1, label, wdg)

    def build(self, data):
        for d in data:
            print(d)
            self.add_arg(**d)

    def delete_children(self):
        for arg in self._args[:]:
            self.pop_arg(arg)

    def on_changed(self, arg, button, *args, **kwargs):
        #Set edit_button visibiliy
        button.setVisible(arg.is_edited())

        #Edit label
        label = self.get_label(arg)
        label.setText(arg("name"))

        self.changed.emit()

    def get_label(self, arg):
        layout = self.layout()
        _idx, _ = layout.getWidgetPosition(arg.wdg.parent())
        lay_item =  layout.itemAt(_idx, QtWidgets.QFormLayout.LabelRole)
        label = lay_item.widget()
        return label

    def get_widget(self, arg):
        layout = self.layout()
        _idx, _ = layout.getWidgetPosition(arg.wdg.parent())
        lay_item =  layout.itemAt(_idx, QtWidgets.QFormLayout.FieldRole)
        wdg = lay_item.widget()
        return wdg

    def export_data(self):
        return self._read()

    def to_data(self):
        return [arg.to_data() for arg in self._args]

    def save_data(self, path):
        data = self.to_data()
        utils.write_json(data, path)