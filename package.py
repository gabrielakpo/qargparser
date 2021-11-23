# -*- coding: utf-8 -*-

name = 'qargparser'

version = '0.5.1'

description = 'Build Qt UI by parsing argument'

authors = ['Gabriel AKPO-ALLAVO']

tools = []

requires = []

build_requires = ['python-2']

_data = {
    "files": {
        "VSCode": {
            "code": ["{root}\\workspaces\\qargparser.code-workspace"]
        }
    }
}

def commands():
    global env
    env.PYTHONPATH.append('{this.root}')
    env.PYTHONPATH.append('{this.root}\\examples')

def pre_commands():
    pass

def post_commands():
    pass

timestamp = 1619380466

format_version = 2

build_command = "python {root}/build.py {install}"