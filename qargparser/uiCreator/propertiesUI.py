from .Qt import QtWidgets, QtCore
from . import utils
from qargparser import ArgParser

class Properties(utils.FrameLayout):
    edited = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        self.ap = ArgParser(label_suffix=':')

        super(Properties, self).__init__(collapsable=False, *args, **kwargs)   

        self.edit_button = QtWidgets.QPushButton("Edit")
        self.reset_button = QtWidgets.QPushButton("Reset")
        self.edit_button.clicked.connect(self.on_edit_cliked)
        self.reset_button.clicked.connect(self.on_reset_cliked)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.edit_button)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.ap)

        #Main
        self.addWidget(scroll_area)
        self.addLayout(buttons_layout)
        
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

    def on_edit_cliked(self):
        data = self.ap.export_data()
        self.arg.update_data(data)
        self.edited.emit()

    def on_reset_cliked(self):
        self.load(self.arg)