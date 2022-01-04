from .Qt import QtWidgets
from .arg import Arg
from .item import Item

class Array(Arg):
    """ Array argument widget. It creates a list of deletables items.
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
        :rtype: :class:`~qargparser.array.Array` instance
    """
    def create(self):
        from .argparser import ArgParser
        wdg = ArgParser(description=self._data['description'])

        self.wdg = wdg
        kwargs = self._data["items"].copy()

        #Item template
        self._item = Item(None, template=kwargs)
        self._item.create()
        self._item.reset_requested.connect(self.on_reset_request)

        #Add items
            #Check max
        defaults = self._data['default']
        if len(defaults)  > self._data["max"]:
            defaults = defaults[:self._data["max"]]

        for default in defaults:
            self.add_item(default)

            #Check min
        remaining = self._data["min"] - len(defaults)
        if remaining > 0:
            for i in range(remaining):
                self.add_item()

        #Add item button
        self.add_item_button = QtWidgets.QPushButton(self._data["buttonLabel"])
        self.add_item_button.clicked.connect(self.add_item)
        layout = self.wdg.layout()
        layout.insertRow(layout.rowCount(), self.add_item_button)

        self._write = None
        self._read = lambda : [arg.read() for arg in wdg._args if arg.read() is not None]
        wdg.changed.connect(self.on_changed)

        return wdg

    def is_edited(self):
        return (len(self.read()) != len(self._data["default"]) 
                or any(child.is_edited() for child in self.wdg._args))

    def add_item(self, default=None):
        idx = len(self.wdg._args)

        #Max
        _max = self._data["max"]
        if _max and idx == _max:
            return

        data = {"type": self._item._data["type"], "template": self._item.to_data()}
        if default:
            data["default"] = default
            
        arg = self.wdg.add_arg(**data)
        arg.delete_requested.connect(self.on_item_delete_resquested)
        self.changed.emit(None)
        return arg

    def on_item_delete_resquested(self, arg):
        #Check min items
        idx = len(self.wdg._args)
        min = self._data.get("min")
        if min and idx == min:
            return

        self.wdg.pop_arg(arg)
        self.changed.emit(None)

    def _init(self):
        kwargs = self._data["items"].copy()
        self._item.update_data({"template": kwargs})

    def reset(self):
        self.wdg.delete_children()
        self._init()

        defaults = self._data['default']
        if len(defaults)  > self._data["max"]:
            defaults = defaults[:self._data["max"]]

        for default in defaults:
            self.add_item(default)

            #Check min
        remaining = self._data["min"] - len(defaults)
        if remaining > 0:
            for i in range(remaining):
                self.add_item()

        self.changed.emit(None)

    def _update(self):
        super(Array, self)._update()
        self.reset()

        #Add Item button
        self.add_item_button.setText(self._data["buttonLabel"])

    def get_children(self):
        return self._item.get_children()

    def to_data(self):
        data = super(Array, self).to_data()
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
        self._data["default"] = []
        self._data["items"] = {}
        self._update()

    def on_reset_request(self):
        self.reset()
        self.reset_requested.emit()

