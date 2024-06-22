from Qt import QtWidgets
from .arg import BlockArg
from .item import Item
from functools import partial
from collections import OrderedDict


class Dict(BlockArg):
    """ Dict argument widget. It creates a list of deletables items.
        You an can add a sub-argument that will be the items template.

        :param default: The default value, defaults to []
        :type default: list of type, optional
        :param min: The minimal number of items, defaults to 0
        :type min: int, optional
        :param max: The maximal number of items, defaults to 10000
        :type max: int, optional
        :param buttonLabel: The label of the add item button , defaults to "Add Items"
        :type buttonLabel: str, optional
        :param items: The item template, defaults to {}
        :type items: {}, optional

        :return: The new instance
        :rtype: :class:`~qargparser.dict.Dict` instance
    """

    def create(self):
        from .argparser import ArgParser
        wdg = ArgParser(description=self._data['description'])
        wdg.layout().setContentsMargins(1, 1, 1, 1)
        wdg.layout().setVerticalSpacing(0)

        self.wdg = wdg
        kwargs = self._data["items"].copy()

        # Item template
        self._item = Item(None, template=kwargs)
        self._item.create()
        self._item.reset_requested.connect(self.on_reset_request)

        # Add items
        # Check max
        defaults = self._data['default']
        if len(defaults.keys()) > self._data["max"]:
            for i in range(self._data["max"]):
                defaults.pop(i)

        for k, v in defaults.items():
            self.add_item(k, v)

            # Check min
        remaining = self._data["min"] - len(defaults)
        if remaining > 0:
            for i in range(remaining):
                self.add_item()

        # Add item button
        self._create_add_item_button()

        self._write = self.__write
        self._read = lambda: OrderedDict([
            (arg._data["_name"], arg.read())
            for arg in wdg._args if arg._data["_name"]])

        wdg.changed.connect(self.on_changed)

        return wdg

    def __write(self, value):
        for i, arg in enumerate(self.wdg._args):
            if arg._write is not None:
                arg._write(value[i])

    def is_edited(self):
        return (len(self.wdg._args) != len(self._data["default"])
                and len(self.wdg._args) > self._data["min"]
                or any(child.is_edited() for child in self.wdg._args))

    def add_item(self, k="", v=""):
        idx = len(self.wdg._args)

        # Max
        _max = self._data["max"]
        if _max and idx == _max:
            return

        data = {"type": self._item._data["type"],
                "template": self._item.to_data()}
        if v:
            data["default"] = v

        arg = self.wdg.add_arg(**data)
        arg._data["_name"] = k

        le = QtWidgets.QLineEdit(arg._data["_name"])
        le.setReadOnly(self._data["readOnly"])
        le.textChanged.connect(partial(self.on_key_text_changed, arg))
        arg.wdg.layout().insertWidget(0, le)

        arg.delete_requested.connect(self.on_item_delete_resquested)
        self.changed.emit(None)
        return arg

    def on_key_text_changed(self, arg, text):
        arg._data["_name"] = text

    def on_item_delete_resquested(self, arg):
        # Check min items
        idx = len(self.wdg._args)
        min = self._data.get("min")
        if min and idx == min:
            return

        self.wdg.pop_arg(arg)
        self.changed.emit(None)

    def _init(self):
        kwargs = self._data["items"].copy()
        self._item.update_data({"template": kwargs})

    def _create_add_item_button(self):
        self.add_item_button = QtWidgets.QPushButton(self._data["buttonLabel"])
        self.add_item_button.clicked.connect(self.add_item)
        layout = self.wdg.layout()
        layout.insertRow(layout.rowCount(), self.add_item_button)
        if self._data["min"] == self._data["max"]:
            self.add_item_button.setVisible(False)

    def reset(self):
        self.wdg.delete_children()
        self._create_add_item_button()
        self._init()

        defaults = self._data['default']
        if len(defaults.keys()) > self._data["max"]:
            for i in range(self._data["max"]):
                defaults.pop(i)

        for k, v in defaults.items():
            self.add_item(k, v)

            # Check min
        remaining = self._data["min"] - len(defaults)
        if remaining > 0:
            for i in range(remaining):
                self.add_item()

        self.changed.emit(None)

    def _update(self):
        super(Dict, self)._update()
        self.reset()

        # Add Item button
        self.add_item_button.setText(self._data["buttonLabel"])

    def get_children(self):
        return self._item.get_children()

    def to_data(self):
        data = super(Dict, self).to_data()
        children = self.get_children()
        if children:
            data["items"] = self._item.to_data()

        return data

    def add_arg(self, *args, **kwargs):
        if len(self._item.item_wdg._args):
            return
        arg = self._item.add_arg(*args, **kwargs)
        self.reset()
        return arg

    def pop_arg(self, *args, **kwargs):
        self._item.pop_arg(*args, **kwargs)
        self._item.update_data({"template": {}})
        self._data["default"] = {}
        self._data["items"] = {}
        self._update()

    def on_reset_request(self):
        self.reset()
        self.reset_requested.emit()
