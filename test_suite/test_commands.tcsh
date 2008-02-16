#!/bin/tcsh -f

set scripts=`pwd`

echo "# Test Setup"
echo  ------------
echo 
source setup_clean.tcsh


echo
echo
echo "# Test Commands"
echo  ------------
echo 
echo
echo pipeline make job test_job
pipeline make job test_job

echo
echo pipeline make sequence test_sequence
pipeline make sequence test_sequence

echo
echo pipeline make shot test_shot
pipeline make shot test_shot

echo
echo pipeline make element test_element
pipeline make element test_element

echo
echo pipeline make extra test_extra
pipeline make extra test_extra

echo
echo pipeline list extra +
pipeline list extra +

echo
echo
echo "# Test Cleanup"
echo  ------------
echo 

cd $scripts
source setup_end.tcsh

