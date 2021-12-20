import sys
from qargparser.uiCreator import show
show(sys.argv[1] if len(sys.argv)>1 else None)      