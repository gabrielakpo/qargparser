# -*- coding: utf-8 -*-

### --- internals

_release_version = '1.3.2'
_dev_version = "dev"

_release_variants = [
    ["python-3.9", "PySide2"], 
    ["python-2", "PySide"]
]


_data = {
    "files": {
        "VSCode": {
            "code": ["{root}\\workspaces\\qargparser.code-workspace"]
        }
    }
}

### --- 

name = 'qargparser'

version = _dev_version
# version = _release_version

description = 'Build Qt UI by parsing argument'

authors = ['Gabriel AKPO-ALLAVO']

tools = ["qargparser_creator"]

requires = []

private_build_requires = ["TBM_RezManager-dev"]

@early()
def variants():
    if this.version != _dev_version: 
        return _release_variants
    else: 
        return []
        
def commands():
    global env
    env.PYTHONPATH.append('{this.root}')
    env.PYTHONPATH.append('{this.root}\\examples')
    env.PATH.append('{this.root}\\bin')

def pre_commands():
    pass

def post_commands():
    pass

timestamp = 1619380466

format_version = 2

build_command = "python {root}/build.py {install}"