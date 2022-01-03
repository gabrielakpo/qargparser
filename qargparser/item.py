from .Qt import QtWidgets, QtCore
from functools import partial
from .arg import Arg

class DeleteButton(QtWidgets.QPushButton):
    def __init__(self, wdg,  label="x", *args, **kwargs):
        super(DeleteButton, self).__init__(label, *args, **kwargs)
        self.wdg = wdg
        self.setFixedWidth(35)

    def paintEvent(self, event):
        super(DeleteButton, self).paintEvent(event)
        height = self.wdg.sizeHint().height()
        if height < 35:
            height = 35
        self.setFixedSize(35, height)
        
class Item(Arg):
    delete_requested = QtCore.Signal(object)

    def create(self):
        from .argparser import ArgParser
        self.item_wdg = ArgParser(description=self._data["description"])

        tpls = self._data["template"] = self._data.get('template', {})
        default = self._data['default']

        if tpls: 
            _tpls = tpls.copy()
            if default is not None:
                _tpls["default"] = default
            _tpls.pop("name", None)
            arg = self.item_wdg.add_arg(**_tpls)
            arg.reset_requested.connect(self.on_reset_request)

        self._read = lambda : self.item_wdg._args[0].read() if len(self.item_wdg._args) else None

        #Delete button
        del_button = DeleteButton(self.item_wdg)
        del_button.clicked.connect(partial(self.delete_requested.emit, self))

        #Main
        self.wdg = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(self.wdg)
        layout.addWidget(self.item_wdg, 0, 0)
        layout.addWidget(del_button, 0, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.item_wdg.changed.connect(self.on_changed)
        self._write = self.item_wdg._write
        return self.wdg

    def reset(self):
        for child in self.get_children():
            child.reset()
            child.changed.emit(None)
        self.changed.emit(None)

    def is_edited(self):
        return any(child.is_edited() for child in self.get_children())

    def get_children(self):
        return self.item_wdg._args

    def to_data(self):
        data = self.item_wdg._args[0].to_data() if len(self.item_wdg._args) else {}
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
