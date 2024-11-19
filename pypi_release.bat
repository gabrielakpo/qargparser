pushd %~dp0
rez env python-3.11 ^
-- bash -c "python setup.py sdist bdist_wheel && python -m twine upload --verbose dist/* -r pypi"

