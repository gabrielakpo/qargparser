from setuptools import setup, find_packages

setup(
    name='qarparser',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "Qt.py"
    ],
    entry_points={
        'console_scripts': [
            # Define console scripts here if needed, e.g.,
            # 'my_command=my_package.module:function',
        ],
    },
    author='gabriel AKPO-ALLAVO',
    author_email='g,allavo@outlook.fr',
    description='fork of `qargparse` made by Motosso',
    # long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gabrielakpo/qargparser',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=2.7',
)
