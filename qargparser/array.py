from .Qt import QtWidgets
from .arg import Arg
from functools import partial

class Array(Arg):
    default = []
    CHILDREN_TYPES = ['array', "item"]
    
    def create(self):
        from .argparser import ArgParser

        wdg = ArgParser(description=self._data['description'])
        kwargs = self._data.get('items', {}).copy()

        self.wdg = wdg

        self._write = None
        self._read = lambda : [arg.read() for arg in wdg._args]
        wdg.changed.connect(self.on_changed)

        #Array
        for default in self._data['default']:
            kwargs['default'] = default
            self.add_item(**kwargs)

        self.child_data = kwargs
        self._create_add_item_button()

        return wdg

    def is_edited(self):
        return len(self.read()) != len(self._data["default"])

    def add_item(self, **kwargs):
        idx = len(self.wdg._args)

        #Max
        _max = self._data.get("max")
        if _max and idx == _max:
            return

        kwargs['name'] = ""
        arg = self.wdg.add_arg(**kwargs)
        arg.deleted.connect(partial(self.on_item_deleted, **kwargs))

        self.changed.emit(None)

    def on_item_deleted(self, **kwargs):
        idx = len(self.wdg._args)
        min = self._data.get("min")
        if min and idx < min:
            self.add_item(**kwargs)

    def _create_add_item_button(self):
        button = QtWidgets.QPushButton('Add item')
        button.clicked.connect(partial(self.add_item, **self.child_data))
        layout = self.wdg.layout()
        layout.insertRow(layout.rowCount(), button)

    def reset(self):
        self.wdg.delete_children()

        kwargs = self._data.get('items', {})

        #Array
        for default in self._data['default']:
            kwargs['default'] = default
            self.add_item(**kwargs)

        self.changed.emit(None)

    def _update(self):
        super(Array, self)._update()
        self.reset()

    def get_children(self):
        return self.wdg._args

    def to_data(self):
        data = super(Array, self).to_data()
        children = self.get_children()
        if children:
            data["items"] = self.get_children()[0].to_data()
        return data

    def add_arg(self, *args, **kwargs):
        if kwargs["type"] in self.CHILDREN_TYPES and not len(self.get_children()):
            self.child_data = kwargs
            if kwargs["type"] == "item":
                return self.wdg.add_arg(*args, **kwargs)
