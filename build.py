#!/usr/bin/env python

import os
import os.path
import shutil
import sys
import compileall

PROJECT = os.environ['REZ_BUILD_PROJECT_NAME']
VERSION = os.environ['REZ_BUILD_PROJECT_VERSION']
EXCLUDES=[
    '__pycache__', 
    '*.py'
]

def compile_package(path, overwrite=True, python2=True):
    if int(sys.version_info[0])>=3:
        succeed=compileall.compile_dir(path, 
                                quiet=0, force=overwrite, legacy=python2)
    else:
        succeed=compileall.compile_dir(path, 
                                quiet=0, force=overwrite)
    return succeed
        
def build(source_path, build_path, install_path, targets):

    def _build():
        source_pkg = os.path.join(source_path, PROJECT)
        build_pkg = os.path.join(build_path, PROJECT)

        #Compile package py
        compile_package(source_pkg)
        
        if os.path.exists(build_pkg):
            shutil.rmtree(build_pkg)
        shutil.copytree(
            source_pkg, 
            build_pkg,
            ignore= shutil.ignore_patterns(*EXCLUDES)
        )

    def _install():
        build_pkg = os.path.join(build_path, PROJECT)
        install_pkg = os.path.join(install_path, PROJECT)
        if os.path.exists(install_pkg):
            shutil.rmtree(install_pkg)
        shutil.copytree(
            build_pkg, 
            install_pkg,
            ignore= shutil.ignore_patterns(*EXCLUDES)
        )

    _build()

    if "install" in (targets or []):
        _install()


if __name__ == '__main__':
    build(
        source_path=os.environ['REZ_BUILD_SOURCE_PATH'],
        build_path=os.environ['REZ_BUILD_PATH'],
        install_path=os.environ['REZ_BUILD_INSTALL_PATH'],
        targets=sys.argv[1:]
    )
