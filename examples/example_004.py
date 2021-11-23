
import sys
import json
import os
from collections import OrderedDict
from qargparser.Qt import QtWidgets, QtCore
from qargparser.argparser import ArgParser
from functools import partial

def print_data(wdg):
    data = wdg.export_data()
    for name in data :
        print(name, data[name])
    
class Window(QtWidgets.QDialog):
    def __init__(self, title=None, data=None):
        super(Window, self).__init__()
        self.setWindowTitle(title)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        win_dow = ArgParser(
            label_suffix=':',
            data=data)
    
        export_data_button = QtWidgets.QPushButton('Export data')
        export_data_button.clicked.connect(partial(print_data, win_dow))
        scroll_area.setWidget(win_dow)

        #Main
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.addWidget(export_data_button)

if __name__ == '__main__':
    here = os.path.dirname(__file__)
    data_file_path = os.path.join(here, 'example_004.json')
    with open(data_file_path, 'r') as f:
        data = json.load(f,  object_pairs_hook=OrderedDict)

    app = QtWidgets.QApplication(sys.argv)
    wdg = Window('Example4', data=data)
    wdg.show()
    sys.exit(app.exec_())
