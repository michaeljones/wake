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
echo pipeline list element + 
pipeline list element + 

echo
echo pipeline make job delete_job
pipeline make job delete_job

echo 
echo pipeline make sequence delete_sequence
pipeline make sequence delete_sequence

echo 
echo pipeline make shot delete_shot
pipeline make shot delete_shot

echo 
echo pipeline make element delete_element
pipeline make element delete_element

echo 
echo pipeline make element delete_element_2
pipeline make element delete_element_2

echo 
echo pipeline make extra delete_extra
pipeline make extra delete_extra

echo
echo pipeline list shot +:+:+
pipeline list shot +:+:+

echo
echo pipeline list element +:+:+:+ 
pipeline list element +:+:+:+ 

echo
echo pipeline list extra +:+:+:+:+
pipeline list extra +:+:+:+:+

/tmp/local/bin/pipeline_web

echo
echo pipeline remove shot delete_shot
pipeline remove shot delete_shot

echo
echo pipeline remove job delete_job
pipeline remove job delete_job

echo
echo
echo "# Test Cleanup"
echo  ------------
echo 

cd $scripts
source setup_end.tcsh

