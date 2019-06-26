#!/bin/sh

function run_tests {
    set -x
    python -c "import ecl3; print(ecl3.__version__)"
}
