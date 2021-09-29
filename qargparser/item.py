from .Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg

class Item(Arg):
    def create(self):
        from .argparser import ArgParser

        item_wdg = ArgParser(description=self._data['description'])
        kwargs = self._data.get('template', {})
        default = self._data['default'] or [""]

        #Array 
        if isinstance(kwargs, list):
            for i, d in enumerate(default):
                _kwargs = kwargs[i].copy()
                _kwargs['default'] = d
                _kwargs['label'] = " "
                item_wdg.add_arg(**_kwargs)

            self._read = lambda : [item_wdg._args[name]._read() \
                                for name in item_wdg._args.keys()] \
                                if len(item_wdg._args.keys()) > 1 \
                                else item_wdg._args.values()[0]._read()
        #Array items
        else:
            for name in kwargs:
                _kwargs = kwargs[name].copy()

                if name in default:
                    _kwargs['default'] = default[name]

                item_wdg.add_arg(name, **_kwargs)

            self._read = lambda : {item_wdg._args[name].name: item_wdg._args[name]._read() \
                                for name in item_wdg._args.keys()}

        self._write = item_wdg._write

        wdg = QtWidgets.QWidget()

        del_button = QtWidgets.QPushButton('x')
        del_button.clicked.connect(partial(self.delete, wdg))

        layout = QtWidgets.QGridLayout(wdg)
        layout.addWidget(item_wdg, 0, 0)
        layout.addWidget(del_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.wdg = wdg

        return wdg

    def delete(self, wdg):
        parent_wdg = wdg.parent()
        parent_wdg.delete_arg(self._data['name'], wdg)
        self.deleted.emit()
        self.changed.emit(None)

    def reset(self):
        self._write(self._data['default'])
        self.changed.emit(None)