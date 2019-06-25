#!/bin/sh

function run_tests {
    set -x
    python -c "import ecl3; print(ecl3.__version__)"
}

function pre_build {
    python -m pip install -r python/requirements-dev.txt

    mkdir build-multibuild
    pushd build-multibuild

    cmake -DBUILD_PYTHON=OFF \
          -DCMAKE_BUILD_TYPE=Release \
          -DBUILD_SHARED_LIBS=ON \
          ..

    sudo make install
    popd

    # clean dirty files from python/, otherwise it picks up the one built
    # outside docker and symbols will be too recent for auditwheel.
    # setuptools_scm really *really* expects a .git-directory. As the wheel
    # building process does its work in /tmp, setuptools_scm crashes because it
    # cannot find the .git dir. Leave version.py so that setuptools can obtain
    # the version from it
    git clean -dxf python --exclude python/ecl3/version.py
}

