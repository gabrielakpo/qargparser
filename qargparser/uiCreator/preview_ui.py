from Qt import QtWidgets, QtCore
from . import envs
from . import utils
from .customs_ui import CustomToolbar


class ReadPreview(QtWidgets.QDialog):
    def __init__(self, data, *args, **kwargs):
        super(ReadPreview, self).__init__(*args, **kwargs)
        self.setWindowTitle("Read Preview")

        wdg = QtWidgets.QPlainTextEdit()
        wdg.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(wdg)

        data = utils.format_json(data)
        wdg.appendPlainText(data)

        self.resize(envs.PREVIEW_WIN_WIDTH,
                    envs.PREVIEW_WIN_HEIGHT)


class PreviewWidget(QtWidgets.QWidget):
    reset_requested = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(PreviewWidget, self).__init__(*args, **kwargs)
        toolbar = CustomToolbar()

        toolbar.addAction(
            envs.ICONS["reset"], "reset", self.on_reset_requested)

        toolbar.addAction(
            envs.ICONS["read_preview"],
            "read preview",
            self.on_read_preview_requested)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(envs.CURRENT_AP)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setSpacing(1)
        self.layout().addWidget(scroll_area)
        self.layout().addWidget(toolbar)

    def on_read_preview_requested(self):
        data = envs.CURRENT_AP.export_data()
        preview_ui = ReadPreview(data, parent=self)
        preview_ui.show()

    def on_reset_requested(self):
        self.reset_requested.emit()
