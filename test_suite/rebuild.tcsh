#!/bin/tcsh -f

# cd ../
# cd foundation

# python setup.py clean
# python setup.py build
# python setup.py bdist_egg

cd ../pipeline

python setup.py clean
python setup.py build
python setup.py bdist_egg

cd ../modules

foreach module ( level development houdini )
	cd $module
	python setup.py clean
	python setup.py build
	python setup.py bdist_egg
	cd ../
end

