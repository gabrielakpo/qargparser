from .Qt import QtWidgets, QtCore
from . import utils, envs
from qargparser import ArgParser
from .customs_ui import CustomToolbar


class PropertiesWidget(QtWidgets.QWidget):
    edited = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        self.arg = None
        self.ap = ArgParser(label_suffix=':')

        super(PropertiesWidget, self).__init__(*args, **kwargs)   

        toolbar = CustomToolbar()
        toolbar.addAction(envs.ICONS["reset"], "reset", self.on_reset_requested)
        toolbar.addAction(envs.ICONS["valid"], "valid", self.on_valid_requested)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ap)

        #Main
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(scroll_area)
        self.layout().addWidget(toolbar)

        self.setDisabled(True)

    def load(self, arg=None):
        self.arg = None
        self.setDisabled(True)
        self.ap.delete_children()

        if not arg: 
            return
        
        data = arg.to_data()

        if arg("type") == "item":
            return 

        self.arg = arg
        self.setDisabled(False)

        _data = utils.get_properties_data(data["type"])

        for d in _data:
            k = d["name"] 
            if not k in data:
                continue
            v = data[k]
            if k in ["enum", "enumDescriptions"]:
                v = [[e] for e in v]
            d["default"] = v
            if k == "default" and "items" in data:
                d["items"] = data["items"]

        self.ap.build(_data)

    def on_valid_requested(self):
        if not self.arg:
            return
        data = self.ap.export_data()
        self.arg.update_data(data)
        self.edited.emit()

    def on_reset_requested(self):
        self.load(self.arg)
