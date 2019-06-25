#!/usr/bin/env python3

import os
import skbuild
import setuptools

def src(x):
    root = os.path.dirname( __file__ )
    return os.path.abspath(os.path.join(root, x))

def getversion():
    pkgversion = { 'version': '0.0.0' }
    versionfile = 'ecl3/version.py'

    if not os.path.exists(versionfile):
        return {
            'use_scm_version': {
                # look for git in ../
                'relative_to' : src('.'),
                # write to ./python
                'write_to'    : os.path.join(src(''), versionfile),
            }
        }

    import ast
    with open(versionfile) as f:
        root = ast.parse(f.read())

    for node in ast.walk(root):
        if not isinstance(node, ast.Assign): continue
        if len(node.targets) == 1 and node.targets[0].id == 'version':
            pkgversion['version'] = node.value.s

    return pkgversion

skbuild.setup(
    name = 'ecl3',
    description = 'ecl3',
    long_description = 'ecl3',
    url = 'https://github.com/equinor/ecl3',
    packages = [
        'ecl3',
    ],
    license = 'LGPL-3.0',
    platforms = 'any',
    install_requires = ['numpy'],
    setup_requires = [
        'setuptools >= 28',
        'pybind11 >= 2.2',
        'setuptools_scm',
        'pytest-runner',
    ],
    tests_require = [
        'pytest',
        'hypothesis',
    ],
    cmake_args = [
        # we can safely pass OSX_DEPLOYMENT_TARGET as it's ignored on
        # everything not OS X. We depend on C++11, which makes our minimum
        # supported OS X release 10.9
        '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.9',
    ],
    # skbuild's test imples develop, which is pretty obnoxious instead, use a
    # manually integrated pytest.
    cmdclass = { 'test': setuptools.command.test.test },
    **getversion()
)
