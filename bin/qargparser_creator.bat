pushd %~dp0
rez env qargparser-dev python-2 PySide -- pythonw -c "import sys;from qargparser.uiCreator import show;show(sys.argv[1] if len(sys.argv)>1 else None)"