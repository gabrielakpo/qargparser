import os
import json
import re
import json
from ..utils import load_data_from_file, write_json
from .Qt import QtWidgets, QtGui, QtCore
from . import envs 

def get_properties_data(name, default=False):
    #Get true file name
    name = envs.PROPERTIES_MAPPING_NAMES.get(name, name)
    #Get base data
    data = load_data_from_file(envs.BASE_PROPERTIES_FILE)
    #Update data
    path = os.path.join(envs.PROPERTIES_PATH, name+".json")
    if os.path.isfile(path):
        data.extend(load_data_from_file(path) or {})

    if default:
        data = {d["name"]: d["default"] for d in data}
    return data

def format_json(data, indent=4):
    return json.dumps(data, indent=indent)

def split_digits(string):
    match = re.match('.*?([0-9]+)$', string)
    if match is not None:
        split = [string.rpartition(match.group(1))[0], match.group(1)]
    else:
        split = [string, None]
    return split

def get_next_name(string):
    n, idx = split_digits(string)
    if not idx:
        idx = "0"
    idx = str(int(idx) + 1)
    return  n + idx

def _load_style():
    path = envs.STYLE_FILE
    with open(path, "r") as f:
        data = f.read()
        data = data.replace('<rootpath>', envs.STYLE_ROOT)
    return _scaled_stylesheet(data)

def _px(value):
    #Get screen resolution
    rec = QtWidgets.QApplication.desktop().screenGeometry()
    h = rec.height()
    factor = h / 2160.0
    return factor * value

def _scaled_stylesheet(ss):
    """Replace any mention of <num>px with scaled version
    This way, you can still use px without worrying about what
    it will look like at HDPI resolution.
    """

    output = []
    for line in ss.splitlines():
        line = line.rstrip()
        if line.endswith("px;"):
            key, value = line.rsplit(" ", 1)
            try:
                value = _px(int(value[:-3]))
                line = "%s %dpx;" % (key, value)
            except:
                pass
        output += [line]
    return "\n".join(output)

def get_example_path(name):
    dir_path = envs.EXAMPLES_DIR_PATH
    path = os.path.join(dir_path, name+envs.EXT)
    return path

class FrameLayout(QtWidgets.QGroupBox):
    def __init__(self, title='', parent=None, collapsable=True):
        super(FrameLayout, self).__init__(title, parent)
        
        self.wdg = QtWidgets.QFrame()
        self.wdg.setFrameShape(QtWidgets.QFrame.Panel)
        self.wdg.setFrameShadow(QtWidgets.QFrame.Plain)
        self.wdg.setLineWidth(0)

        wdg_layout = QtWidgets.QVBoxLayout(self.wdg)
        wdg_layout.setContentsMargins(0, 10, 0, 0)
        wdg_layout.setSpacing(0)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        super(FrameLayout, self).setLayout(layout)
        layout.addWidget(self.wdg)
         
        self.is_colapsed = False
        self.is_collapsable = collapsable
        self.offset = 25

    def setLayout(self, layout):
        self.wdg.setLayout(layout)
         
    def expandCollapseRect(self):
        return QtCore.QRect(0, 0, self.width(), 20)
 
    def mouseReleaseEvent(self, event):
        if self.expandCollapseRect().contains(event.pos()):
            self.toggleCollapsed()
            event.accept()
        else:
            event.ignore()
     
    def toggleCollapsed(self):
        self.setCollapsed(not self.is_colapsed)

    def setCollapsable(self, value):
        self.is_collapsable = bool(value)
         
    def setCollapsed(self, state=True):
        if not self.is_collapsable:
            return 

        self.is_colapsed = state
 
        if state:
            self.setMaximumHeight(20)
            self.wdg.setMaximumHeight(0)
            self.wdg.setHidden(True)
        else:
            self.setMaximumHeight(1000000)
            self.wdg.setMaximumHeight(1000000)
            self.wdg.setHidden(False)

    def addWidget(self, *args, **kwargs):
        self.wdg.layout().addWidget(*args, **kwargs)
     
    def addLayout(self, *args, **kwargs):
        self.wdg.layout().addLayout(*args, **kwargs)

    def setSpacing(self, value):
        self.wdg.layout().setSpacing(value)

    def addStretch(self, value):
        self.wdg.layout().addStretch(value)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
         
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
 
        x = self.rect().x()
        y = self.rect().y()
        w = self.rect().width()
         
        painter.setRenderHint(painter.Antialiasing)
        painter.fillRect(self.expandCollapseRect(), QtGui.QColor(93, 93, 93))
        painter.drawText(
            x, y + 3, w, 16,
            QtCore.Qt.AlignCenter| QtCore.Qt.AlignTop,
            self.title())
        self.drawTriangle(painter, x, y)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
        painter.end()
         
    def drawTriangle(self, painter, x, y):     
        if not self.is_collapsable:
            return 

        if not self.is_colapsed:
            points = [  QtCore.QPoint(x+10,  y+6 ),
                        QtCore.QPoint(x+20, y+6 ),
                        QtCore.QPoint(x+15, y+11) ]
             
        else:
            points = [  QtCore.QPoint(x+10, y+4 ),
                        QtCore.QPoint(x+15, y+9 ),
                        QtCore.QPoint(x+10, y+14)]
        currentBrush = painter.brush()
        currentPen = painter.pen()
         
        painter.setBrush(
            QtGui.QBrush(
                QtGui.QColor(187, 187, 187),
                QtCore.Qt.SolidPattern))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.drawPolygon(QtGui.QPolygon(points))
        painter.setBrush(currentBrush)
        painter.setPen(currentPen)
