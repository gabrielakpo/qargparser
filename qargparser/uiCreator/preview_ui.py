from .Qt import QtWidgets, QtCore
from . import envs
from . import utils
from .customs_ui import CustomToolbar

class ReadPreview(QtWidgets.QWidget):
    def __init__(self, data, *args, **kwargs):
        super(ReadPreview, self).__init__(*args, **kwargs)
        self.setWindowTitle("Read Preview")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        wdg = QtWidgets.QPlainTextEdit()
        wdg.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(wdg)

        data = utils.format_json(data)
        wdg.appendPlainText(data)

        self.resize(envs.PREVIEW_WIN_WIDTH, 
                    envs.PREVIEW_WIN_HEIGHT)

        self.show()
        self.move(self.parent().x(), self.parent().y())

class PreviewWidget(QtWidgets.QGroupBox):
    def __init__(self, title="PREVIEW", *args, **kwargs):
        super(PreviewWidget, self).__init__(title, *args, **kwargs)   
        self.setAlignment(QtCore.Qt.AlignCenter)

        toolbar = CustomToolbar()
        toolbar.addAction(envs.ICONS["read_preview"], "read preview", self.on_read_preview_requested)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(envs.CURRENT_AP)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(scroll_area)
        self.layout().addWidget(toolbar)

    def on_read_preview_requested(self):
        data = envs.CURRENT_AP.export_data()
        ReadPreview(data, parent=self)
