from .Qt import QtWidgets
from .arg import Arg
from functools import partial

class Array(Arg):
    default = []

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
            
        self._create_add_item_button(**kwargs)

        return wdg

    def is_edited(self):
        return len(self.read()) != len(self._data["default"])

    def add_item(self, **kwargs):
        idx = len(self.wdg._args)

        #Max
        max = self._data.get("max")
        if max and idx == max:
            return

        #Generate name
        name = self._data['name']
        n = name

        while(True):
            if n not in self.wdg._args:
                break
            idx +=1
            n = name + str(idx)

        kwargs['label'] = ' '
        arg = self.wdg.add_arg(n, **kwargs)
        arg.deleted.connect(partial(self.on_item_deleted, **kwargs))

        self.changed.emit(None)

    def on_item_deleted(self, **kwargs):
        idx = len(self.wdg._args)

        #Min
        min = self._data.get("min")

        if min and idx < min:
            self.add_item(**kwargs)

    def _create_add_item_button(self, **kwargs):
        button = QtWidgets.QPushButton('Add item')
        button.clicked.connect(partial(self.add_item, **kwargs))
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

    def get_children(self):
        return self.wdg._args