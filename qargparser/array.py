from .Qt import QtWidgets
from .arg import Arg
from functools import partial

class Array(Arg):
    default = []

    def create(self):
        from .argparser import ArgParser
        wdg = ArgParser(description=self._data['description'])
        kwargs = self._data.get('items', {}).copy()
        name = self._data['name']

        #Array
        if kwargs.get('type') == 'array':
            for n in self._data['default']:
                idx = len(wdg._arguments)
                wdg.add_argument(name + str(idx), **kwargs)
        else:
            kwargs['type'] = 'item'
            kwargs['label'] = ' '

            for default in self._data['default']:
                kwargs['default'] = default
                idx = len(wdg._arguments)
                arg = wdg.add_argument(name + str(idx),**kwargs)
                arg.deleted.connect(partial(self.on_item_deleted, **kwargs))
            
        self.wdg = wdg
        self.add_item_button = QtWidgets.QPushButton('Add item')
        self.add_item_button.clicked.connect(partial(self.add_item, **kwargs))
        layout = wdg.layout()
        layout.addWidget(self.add_item_button, layout.rowCount(), 1)

        self._write = None
        self._read = lambda : [wdg._arguments[name]._read() for name in wdg._arguments]
        wdg.changed.connect(self.on_changed)

        return wdg

    def is_edited(self):
        return len(self.read()) != len(self._data["default"])

    def add_item(self, **kwargs):
        idx = len(self.wdg._arguments)

        #Max
        max = self._data.get("max")
        if max and idx == max:
            return

        #Generate name
        name = self._data['name']
        n = name

        while(True):
            if n not in self.wdg._arguments:
                break
            idx +=1
            n = name + str(idx)

        kwargs['default'] = self._data['items'].get('default', '')
        arg = self.wdg.add_argument(n, **kwargs)
        arg.deleted.connect(partial(self.on_item_deleted, **kwargs))

        self.changed.emit(None)

    def on_item_deleted(self, **kwargs):
        idx = len(self.wdg._arguments)

        #Min
        min = self._data.get("min")

        if min and idx < min:
            self.add_item(**kwargs)

    def reset(self):
        self.wdg.delete_children()
        wdg = self.wdg
        kwargs = self._data.get('items', {})
        name = self._data['name']

        #Array
        if kwargs.get('type') == 'array':
            for n in self._data['default']:
                kwargs['default'] = n
                idx = len(wdg._arguments)
                wdg.add_argument(name + str(idx), **kwargs)
        else:
            kwargs['type'] = 'item'
            kwargs['label'] = ' '

            for default in self._data['default']:
                kwargs['default'] = default
                idx = len(wdg._arguments)
                arg = wdg.add_argument(name + str(idx), **kwargs)
                arg.deleted.connect(partial(self.on_item_deleted, **kwargs))

        self.add_item_button = QtWidgets.QPushButton('Add item')
        self.add_item_button.clicked.connect(partial(self.add_item, **kwargs))
        layout = wdg.layout()
        layout.addWidget(self.add_item_button, layout.rowCount(), 1)

        self.changed.emit(None)
