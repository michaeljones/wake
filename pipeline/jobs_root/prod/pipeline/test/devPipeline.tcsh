#!/bin/tcsh -f 

cd

# Remove old version
if( -e /tmp/pipeline) then
	rm -fr /tmp/pipeline
endif

rm -f ~/.last

# Clean out mysql table
mysql -u pipeline -ppipeline << ENDCAT
use pipeline;
DROP TABLE IF EXISTS test_levels;
DROP TABLE IF EXISTS test_nodes;
ENDCAT


# Copy over fresh one
cp -r ~/projects/pipeline/repos/pipeline /tmp/pipeline

# Edit environment file to comment out any other version
# and clean up any old lines
sed -i 's/^pushd/# pushd/g' ~/.environment
sed -i 's/^# pushd \/tmp\/pipeline\/jobs_root.*$//g' ~/.environment

# Add in necessary line for sourcing pipeline_setup
echo "pushd /tmp/pipeline/jobs_root > /dev/null; source .pipeline_setup; popd > /dev/null;" >> ~/.environment


# Move to the lib directory
cd /tmp/pipeline/jobs_root/prod/pipeline/lib

sed -i 's/^table_prefix.*$/table_prefix = "test_"/g' settings.py
sed -i 's/^env_prefix.*$/env_prefix = "TEST_"/g' settings.py

# Move to the scripts directory
cd /tmp/pipeline/jobs_root/prod/pipeline/scripts

# Run the install script
python setup.py install




