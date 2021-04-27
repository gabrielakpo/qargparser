
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

here = os.path.dirname(__file__)
data_file_path = os.path.join(here, 'example_001.json')

app = QtWidgets.QApplication(sys.argv)

with open(data_file_path, 'r') as f:
    data = json.load(f,  object_pairs_hook=OrderedDict)

wdg = QtWidgets.QWidget()
scroll_area = QtWidgets.QScrollArea()
scroll_area.setWidgetResizable(True)
title_label = QtWidgets.QLabel('Create package')
title_label.setAlignment(QtCore.Qt.AlignCenter)
win_dow = ArgParser(
    label_suffix=':',
    data=data,
    description='Create package')
export_data_button = QtWidgets.QPushButton('Export data')
export_data_button.clicked.connect(partial(print_data, win_dow))
scroll_area.setWidget(win_dow)
layout = QtWidgets.QVBoxLayout(wdg)
layout.addWidget(title_label)
layout.addWidget(scroll_area)
layout.addWidget(export_data_button)
wdg.show()
sys.exit(app.exec_())

# import types

# def string_to_function(text):
#     code = compile(text, '<string>', 'exec')
#     fct = types.FunctionType(code.co_consts[0], globals())
#     return fct

# command = string_to_function('def command():\n\timport os\n\tprint(os)')
# command()