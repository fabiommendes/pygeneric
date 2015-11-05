#!/bin/sh
echo "starting p2install..." && ./tests.sh &&
rm py2src -rf &&
echo "removed old py2src" &&
cp src py2src -r &&
echo "copy src and start 3to2 conversion" &&
3to2 py2src/ --no-diffs -j4 -w -f kwargs -f division -f metaclass -f annotations &&
echo "\n\nend 3to2\n\n" &&
python2 setup.py install --user &&
python2 -m generic.tests
