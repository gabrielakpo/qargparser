from .Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg

class Item(Arg):

    def create(self):
        from .argparser import ArgParser

        item_wdg = ArgParser(description=self._data['description'])
        kwargs = self._data.get('template', {}).copy()

        #Array
        default = self._data['default'] or []

        #Update 
        for name in kwargs:
            _kwargs = kwargs[name].copy()

            if name in default:
                _kwargs['default'] = default[name]

            arg = item_wdg.add_arg(name, **_kwargs)
            # arg.deleted.connect(partial(self.on_item_deleted, **_data))

        wdg = QtWidgets.QWidget()

        del_button = QtWidgets.QPushButton('X')
        del_button.clicked.connect(partial(self.delete, wdg))

        layout = QtWidgets.QGridLayout(wdg)
        layout.addWidget(item_wdg, 0, 0)
        layout.addWidget(del_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.wdg = wdg
        self._write = item_wdg._write
        self._read = lambda : {item_wdg._args[name].name: item_wdg._args[name]._read() for name in item_wdg._args.keys()}

        return wdg

    def delete(self, wdg):
        parent_wdg = wdg.parent()
        parent_wdg.delete_arg(self._data['name'], wdg)
        self.deleted.emit()
        self.changed.emit(None)

    def add_item(self, **kwargs):
        idx = len(self.wdg._args)
        name = self._data['name']
        self.wdg.add_arg(name + str(idx), **kwargs)

    def reset(self):
        self._write(self._data['default'])
        self.changed.emit(None)