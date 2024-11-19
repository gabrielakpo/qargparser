from Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg
from . import envs


class DeleteButton(QtWidgets.QPushButton):
    def __init__(self, wdg,  label="x", *args, **kwargs):
        super(DeleteButton, self).__init__(label, *args, **kwargs)
        self.wdg = wdg

    def paintEvent(self, event):
        super(DeleteButton, self).paintEvent(event)
        height = self.wdg.sizeHint().height()
        if height < envs.ITEM_DEL_BUTTON_MIN_HEIGHT:
            height = envs.ITEM_DEL_BUTTON_MIN_HEIGHT
        self.setFixedSize(envs.ITEM_DEL_BUTTON_WIDTH, height)


class Item(Arg):
    delete_requested = QtCore.Signal(object)

    def create(self):
        from .argparser import ArgParser
        self.item_wdg = ArgParser(description=self._data["description"])
        self.item_wdg.layout().setContentsMargins(0, 0, 0, 0)
        self.item_wdg.layout().setVerticalSpacing(0)

        tpls = self._data["template"] = self._data.get('template', {})
        default = self._data['default']

        if tpls:
            _tpls = tpls.copy()
            if default is not None:
                _tpls["default"] = default
            _tpls.pop("name", None)
            arg = self.item_wdg.add_arg(**_tpls)
            arg.reset_requested.connect(self.on_reset_request)

        self._read = lambda: self.item_wdg._args[0].read() if len(
            self.item_wdg._args) else None
        self._write = self.__write

        # Delete button
        del_button = DeleteButton(self.item_wdg)
        del_button.clicked.connect(partial(self.delete_requested.emit, self))

        # Main
        self.wdg = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(self.wdg)
        layout.addWidget(self.item_wdg)
        layout.addWidget(del_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.item_wdg.changed.connect(self.on_changed)
        return self.wdg

    def __write(self, value):
        for arg in self.item_wdg._args:
            arg._write(value)

    def reset(self):
        for child in self.item_wdg._args:
            child.reset()
            child.changed.emit(None)
        self.changed.emit(None)

    def is_edited(self):
        return any(child.is_edited() for child in self.item_wdg._args)

    def get_children(self):
        return self.item_wdg._args

    def to_data(self):
        data = self.item_wdg._args[0].to_data() if len(
            self.item_wdg._args) else {}
        return data

    def add_arg(self, *args, **kwargs):
        return self.item_wdg.add_arg(*args, **kwargs)

    def pop_arg(self, *args, **kwargs):
        self.item_wdg.pop_arg(*args, **kwargs)
        self._data['default'] = None
        self._update()

    def on_reset_request(self):
        self.reset()
        self.reset_requested.emit()
