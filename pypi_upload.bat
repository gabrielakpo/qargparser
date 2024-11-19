pushd %~dp0
rez env python-3.11 ^
-- python -m twine upload --verbose dist/* -r pypi
