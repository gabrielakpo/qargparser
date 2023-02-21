import sys
from qargparser.uiCreator.main_ui import show
show(sys.argv[1] if len(sys.argv)>1 else None)      