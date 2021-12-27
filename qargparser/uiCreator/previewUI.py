from .Qt import QtWidgets

class Preview(QtWidgets.QGroupBox):
    def __init__(self, ap, *args, **kwargs):
        super(Preview, self).__init__(*args, **kwargs)   
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(ap)
        layout.addWidget(scroll_area)