# -*- coding: utf-8 -*-


# ---

name = 'qargparser'

version = '1.4'

description = 'Build Qt UI by parsing argument'

authors = ['Gabriel AKPO-ALLAVO']

tools = ["qargparser_creator"]

requires = ["python", "Qt.py"]

private_build_requires = ["TBM_RezManager-dev"]


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


_data = {
    "files": {
        "VSCode": {
            "code": ["{root}\\workspaces\\qargparser.code-workspace"]
        }
    }
}
