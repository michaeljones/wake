#!/bin/tcsh -f

cd ../
cd foundation

python setup.py clean
python setup.py build
python setup.py bdist_egg

cd ../pipeline

python setup.py clean
python setup.py build
python setup.py bdist_egg

cd ../modules

cd level

python setup.py clean
python setup.py build
python setup.py bdist_egg


