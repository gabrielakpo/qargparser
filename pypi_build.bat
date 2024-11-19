pushd %~dp0
rez env python-3.11 ^
-- python setup.py sdist bdist_wheel


