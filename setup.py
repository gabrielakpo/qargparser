from setuptools import setup, find_packages
import os

def read(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, "r") as f:
        return f.read()


setup(
    name='qargparser',
    version='0.0.1',
    packages=find_packages(
        include=['*'],  # ['*'] by default
        exclude=["*.pyc", "__pycache__"],  # empty by default
        ),
    install_requires=[
        "Qt.py"
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            # Define console scripts here if needed, e.g.,
            # 'my_command=my_package.module:function',
        ],
    },
    author='gabriel AKPO-ALLAVO',
    author_email='g.allavo@outlook.fr',
    description='fork of `qargparse` made by Motosso',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/gabrielakpo/qargparser',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license=read("LICENSE"),
    python_requires='>=2.7',
)
