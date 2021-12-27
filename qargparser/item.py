from .Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg

class Item(Arg):
    def create(self):
        from .argparser import ArgParser
        self.item_wdg = ArgParser(description=self._data['description'])

        kwargs = self._data.get('template', {})
        default = self._data['default'] or [""]

        #Array 
        if isinstance(kwargs, list):
            for i, d in enumerate(default):
                _kwargs = kwargs[i].copy()
                _kwargs['default'] = d
                _kwargs['label'] = " "
                self.item_wdg.add_arg(**_kwargs)

            self._read = lambda : [arg.read() for arg in self.item_wdg._args] \
                                if len(self.item_wdg._args) > 1 \
                                else self.item_wdg._args[0]._read()
        #Array items
        else:
            for name in kwargs:
                _kwargs = kwargs[name].copy()

                if name in default:
                    _kwargs['default'] = default[name]

                self.item_wdg.add_arg(name, **_kwargs)

            self._read = lambda : {arg.name: arg.read() for arg in self.item_wdg._args}

        self._write = self.item_wdg._write

        wdg = QtWidgets.QWidget()

        #Delete button
        del_button = QtWidgets.QPushButton('x')
        del_button.setFixedWidth(50)
        del_button.clicked.connect(partial(self.delete_item, wdg))

        #Main
        layout = QtWidgets.QGridLayout(wdg)
        layout.addWidget(self.item_wdg, 0, 0)
        layout.addWidget(del_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.wdg = wdg
        return wdg

    def delete_item(self, wdg):
        parent_wdg = wdg.parent().parent()
        parent_wdg.pop_arg(self)
        self.deleted.emit()
        self.changed.emit(None)

    def reset(self):
        self._write(self._data['default'])
        self.changed.emit(None)

    def get_children(self):
        return self.item_wdg._args