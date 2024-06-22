from functools import partial
from collections import OrderedDict
from Qt import QtWidgets, QtCore, QtGui
from .object import Object
from .tab import Tab
from .string import String, Info
from .text import Text, Doc, Code, Python, Mel
from .array import Array
from .number import Float, Integer
from .item import Item
from .boolean import Boolean
from .path import Path
from .enum import Enum
from .color import Color
from .dict import Dict
from . import utils, envs
import re

TYPES = {
    "object": Object,
    "tab": Tab,
    "enum": Enum,
    "info": Info,
    "string": String,
    "text": Text,
    "doc": Doc,
    "dict": Dict,
    "path": Path,
    "code": Code,
    "mel": Mel,
    "python": Python,
    "array": Array,
    "boolean": Boolean,
    "float": Float,
    "integer": Integer,
    "color": Color,
}

_TYPES = TYPES.copy()
_TYPES.update({
    "item": Item,
    "bool": Boolean,
    "int": Integer,
    "str": String,
    "unicode": String
})


def deleteChildWidgets(item):
    layout = item.layout()
    if layout:
        for i in range(layout.count()):
            deleteChildWidgets(layout.itemAt(i))
    if item.widget():
        item.widget().deleteLater()


def clear_layout(layout):
    """Delete all UI children recurcively

    :param layout: layout parent, defaults to None
    :type layout: QLayout, optional
    """

    while layout.count():
        item = layout.takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.deleteLater()
            lay = item.layout()
            if lay:
                clear_layout(lay)


def get_object_from_type(type):
    return _TYPES[type]


class ResetButton(QtWidgets.QPushButton):
    def __init__(self, wdg, *args, **kwargs):
        super(ResetButton, self).__init__(QtGui.QIcon(envs.RELOAD_ICON),
                                          "",
                                          *args, **kwargs)
        self.setIconSize(QtCore.QSize(envs.RELOAD_BUTTON_ICON_SIZE,
                                      envs.RELOAD_BUTTON_ICON_SIZE))
        self.wdg = wdg

    def paintEvent(self, event):
        super(ResetButton, self).paintEvent(event)
        height = self.wdg.sizeHint().height()
        if height < envs.RELOAD_BUTTON_MIN_HEIGHT:
            height = envs.RELOAD_BUTTON_MIN_HEIGHT
        self.setFixedSize(envs.RELOAD_BUTTON_WIDTH, height)


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
            txt = "%s%s " % (txt, self.label_suffix)
        return txt


class ArgParser(QtWidgets.QWidget):
    """ Generates argument widget instances parented in its layout.
        You can read its values or save its build data in a .json file
        and use it to recreate this widget.
        There are the different argument widget types :

        :class:`~qargparser.array.Array` 
        :class:`~qargparser.boolean.Boolean`
        :class:`~qargparser.enum.Enum` 
        :class:`~qargparser.number.Integer`
        :class:`~qargparser.number.Float`
        :class:`~qargparser.object.Object`
        :class:`~qargparser.path.Path`
        :class:`~qargparser.string.String`
        :class:`~qargparser.string.Info`
        :class:`~qargparser.text.Text`
        :class:`~qargparser.text.Doc`
        :class:`~qargparser.text.Python`
        :class:`~qargparser.text.Mel`

        :param data: The build data, defaults to None
        :type data: dict, optional
        :param label_suffix: The suffix for sub_widgets labels,
                             defaults to None
        :type label_suffix: str, optional
        :param description: The description of the widget, defaults to ""
        :type description: str, optional
        :param parent: The description of the widget, defaults to None
        :type parent: QWidget instance, optional

        :return: The new instance
        :rtype: :class:`~qargparser.argparser.ArgParser` instance
    """
    changed = QtCore.Signal()

    def __init__(self,
                 data=None,
                 path=None,
                 label_suffix=None,
                 description="",
                 parent=None):

        # Init
        self._description = description
        self._label_suffix = label_suffix
        self._args = []

        super(ArgParser, self).__init__(parent)

        self.setContentsMargins(2, 5, 2, 5)

        # Layout
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setFormAlignment(QtCore.Qt.AlignTop)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.setVerticalSpacing(5)

        # build from path
        if path:
            self.build_from_path(path)
        # build from data
        elif data:
            self.build(data)

        self._write = lambda *args, **kwargs: (arg._write(*args, **kwargs)
                                               for arg in self._args)
        self._read = lambda: OrderedDict(
            (arg("name"), arg._read()) for arg in self._args
            if arg._data.get("optional") is None
            or arg.wdg.parent().isChecked())

    def __repr__(self):
        return "<{}( {} )>".format(self.__class__.__name__, self._args)

    @property
    def _row(self):
        return len(self._args)

    def add_arg(self,
                name=None,
                type=None,
                default=None,
                **kwargs):
        """Adds an argument.

        :param name: The argument name, defaults to None
        :type name: str, optional
        :param type: The type of the argument
                     ["object", "enum", "info", "string",
                     "text", "doc","path", "mel", 
                     "python", "array", "item", "boolean", 
                     "float, "integer"], defaults to None
        :type type: str, optional
        :param default: The default value, defaults to None
        :type default: type, optional
        :return: The new argument instance
        :rtype: :class:`~qargparser.array.Array` ,
                :class:`~qargparser.boolean.Boolean`,
                :class:`~qargparser.enum.Enum` ,
                :class:`~qargparser.number.Integer`,
                :class:`~qargparser.number.Float`,
                :class:`~qargparser.object.Object`,
                :class:`~qargparser.path.Path`,
                :class:`~qargparser.string.String`,
                :class:`~qargparser.string.Info`,
                :class:`~qargparser.text.Text`,
                :class:`~qargparser.text.Doc`,
                :class:`~qargparser.text.Python`
                or
                :class:`~qargparser.text.Mel` instance
        """

        arg = get_object_from_type(type)(name,
                                         default,
                                         **kwargs)

        self._add_arg(arg)
        return arg

    def _add_arg(self, arg):
        # name = arg._data["name"]
        # if self.get_arg(name):
        #     raise ValueError("Duplicate argument "%s"" %name)

        # Create widget
        wdg = arg.create()
        desc = arg._data.get("description")
        if desc.strip():
            wdg.setToolTip(utils.pretty_description(desc))

        # Reset
        reset_button = ResetButton(wdg)
        reset_button.clicked.connect(arg.reset)
        arg.changed.connect(partial(self.on_changed, arg, reset_button))
        reset_button.setVisible(False)

        # add widget to Layout
        layout = self.layout()
        label = arg._data["name"]

        label_ui = CustomLabel(label, label_suffix=self._label_suffix)

        optional = arg._data.get("optional")
        if optional is not None:
            row_wdg = QtWidgets.QGroupBox()
            row_wdg.setCheckable(True)
            row_wdg.setChecked(optional)
        else:
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
        """Gets an argument from a name or an index.

        :param key: The argument name or its index
        :type key: str, int
        :return: The argument
        :rtype: :class:`~qargparser.array.Array` ,
                :class:`~qargparser.boolean.Boolean`,
                :class:`~qargparser.enum.Enum` ,
                :class:`~qargparser.number.Integer`,
                :class:`~qargparser.number.Float`,
                :class:`~qargparser.object.Object`,
                :class:`~qargparser.path.Path`,
                :class:`~qargparser.string.String`,
                :class:`~qargparser.string.Info`,
                :class:`~qargparser.text.Text`,
                :class:`~qargparser.text.Doc`,
                :class:`~qargparser.text.Python`
                or
                :class:`~qargparser.text.Mel` instance
        """
        for i, arg in enumerate(self._args):
            if ((isinstance(key, int) and i == key)
                    or (isinstance(key, str) and arg("name") == key)):
                return arg

    def get_args(self):
        """Gets all arguments.
        :return: The arguments
        :rtype: list of :class:`~qargparser.array.Array` ,
                :class:`~qargparser.boolean.Boolean`,
                :class:`~qargparser.enum.Enum` ,
                :class:`~qargparser.number.Integer`,
                :class:`~qargparser.number.Float`,
                :class:`~qargparser.object.Object`,
                :class:`~qargparser.path.Path`,
                :class:`~qargparser.string.String`,
                :class:`~qargparser.string.Info`,
                :class:`~qargparser.text.Text`,
                :class:`~qargparser.text.Doc`,
                :class:`~qargparser.text.Python`
                or
                :class:`~qargparser.text.Mel` instance
        """
        return self._args

    def pop_arg(self, arg):
        """Removes an argument.

        :param arg: The argument
        :type arg:  :class:`~qargparser.array.Array` ,
                    :class:`~qargparser.boolean.Boolean`,
                    :class:`~qargparser.enum.Enum` ,
                    :class:`~qargparser.number.Integer`,
                    :class:`~qargparser.number.Float`,
                    :class:`~qargparser.object.Object`,
                    :class:`~qargparser.path.Path`,
                    :class:`~qargparser.string.String`,
                    :class:`~qargparser.string.Info`,
                    :class:`~qargparser.text.Text`,
                    :class:`~qargparser.text.Doc`,
                    :class:`~qargparser.text.Python`
                    or
                    :class:`~qargparser.text.Mel` instance
        """
        layout = self.layout()
        idx, _ = layout.getWidgetPosition(arg.wdg.parent())

        # Label
        lay_item = layout.itemAt(idx, QtWidgets.QFormLayout.LabelRole)
        deleteChildWidgets(lay_item)
        layout.removeItem(lay_item)

        # widget
        lay_item = layout.itemAt(idx, QtWidgets.QFormLayout.FieldRole)
        deleteChildWidgets(lay_item)
        layout.removeItem(lay_item)

        self._args.remove(arg)

    def move_arg(self, key, idx):
        """Move an argument from itself or its index to a target index.

        :param key: The argument or its index
        :type key:  :class:`~qargparser.array.Array` ,
                    :class:`~qargparser.boolean.Boolean`,
                    :class:`~qargparser.enum.Enum` ,
                    :class:`~qargparser.number.Integer`,
                    :class:`~qargparser.number.Float`,
                    :class:`~qargparser.object.Object`,
                    :class:`~qargparser.path.Path`,
                    :class:`~qargparser.string.String`,
                    :class:`~qargparser.string.Info`,
                    :class:`~qargparser.text.Text`,
                    :class:`~qargparser.text.Doc`,
                    :class:`~qargparser.text.Python`
                    :class:`~qargparser.text.Mel` instance,
                    int
        :param idx: The target index
        :type idx: int
        """
        if isinstance(key, int):
            key = self._args[key]

        label = self.get_label(key)
        label.setParent(None)

        wdg = self.get_widget(key)
        wdg.setParent(None)

        self._args.remove(key)
        self._args.insert(idx, key)

        layout = self.layout()

        _idx = 0
        if idx > 0:
            if idx >= len(self._args) - 1:
                _idx = layout.rowCount()
            else:
                _idx = layout.getWidgetPosition(
                    self._args[idx+1].wdg.parent())[0] - 1

        layout.insertRow(_idx+1, label, wdg)

    def build(self, data):
        """Build itself from data.

        :param data: The data
        :type data: dict
        """
        for d in data:
            self.add_arg(**d)

    def build_from_path(self, path):
        data = utils.load_data_from_file(path)
        if not data:
            raise RuntimeError("Error reading data")
        self.clear()
        self.build(data)

    def delete_children(self):
        """Deletes all children arguments.
        """
        clear_layout(self.layout())
        self._args = []

    def clear(self):
        self.delete_children()

    def on_changed(self, arg, button, *args, **kwargs):
        # Set edit_button visibiliy
        button.setVisible(arg.is_edited())

        # Edit label
        label = self.get_label(arg)
        label.setText(arg("name"))

        self.changed.emit()

    def get_label(self, arg):
        layout = self.layout()
        _idx, _ = layout.getWidgetPosition(arg.wdg.parent())
        lay_item = layout.itemAt(_idx, QtWidgets.QFormLayout.LabelRole)
        label = lay_item.widget()
        return label

    def get_widget(self, arg):
        layout = self.layout()
        _idx, _ = layout.getWidgetPosition(arg.wdg.parent())
        lay_item = layout.itemAt(_idx, QtWidgets.QFormLayout.FieldRole)
        wdg = lay_item.widget()
        return wdg

    def export_data(self):
        return self._read()

    def read(self):
        """Read all arguments values.

        :return: The values read
        :rtype: dict
        """
        return self._read()

    def to_data(self):
        """Gets its data.

        :return: The data
        :rtype: dict
        """
        return [arg.to_data() for arg in self._args]

    def save_data(self, path):
        """Saves its data to a path.

        :param path: The path
        :type path: str
        """
        data = self.to_data()
        utils.write_json(data, path)

    def erase_data(self):
        for arg in self.get_args():
            arg.erase_data()
            arg.reset()

    def reset(self):
        for arg in self.get_args():
            arg.reset()
