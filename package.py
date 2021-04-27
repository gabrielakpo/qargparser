# -*- coding: utf-8 -*-

name = 'qargparser'

version = 'dev'

description = 'Build Qt UI by parsing argument'

authors = ['Gabriel AKPO-ALLAVO']

tools = []

requires = []

build_requires = ['python-2']

def commands():
    global env
    env.PYTHONPATH.append('{this.root}')

def pre_commands():
    pass

def post_commands():
    pass

timestamp = 1619380466

format_version = 2

build_command = "python {root}/build.py {install}"