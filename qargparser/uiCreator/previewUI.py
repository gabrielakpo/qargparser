from .Qt import QtWidgets
from . import utils

class Preview(utils.FrameLayout):
    def __init__(self, ap, *args, **kwargs):
        super(Preview, self).__init__(collapsable=False, *args, **kwargs)   
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(ap)
        self.addWidget(scroll_area)