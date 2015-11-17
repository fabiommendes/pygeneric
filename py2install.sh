#!/bin/sh
echo "starting p2install..." &&
    rm py2src -rf &&
    echo "removed old py2src" &&
    cp src py2src -r &&
    echo "copy src and start 3to2 conversion" &&
    sh 3to2.sh &&
    echo "\n\nend 3to2\n\n" &&
    python2 setup.py install --user &&
    py.test-2.7 py2src -q
