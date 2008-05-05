#!/bin/tcsh -f

cd /tmp/

set pyVer=2.5

setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games
setenv PYTHONPATH /tmp/local/lib/python${pyVer}/site-packages
# mkdir -p local/lib/python${pyVer}/site-packages 

cp -r /home/mike/projects/pipeline/modular/dependencies /tmp/local

# easy_install --prefix local http://www.michaelpjones.co.uk/pipeline/SlipStream_foundation-0.0.1-py${pyVer}.egg
# easy_install --prefix local http://www.michaelpjones.co.uk/pipeline/SlipStream-0.0.1-py${pyVer}.egg
# easy_install --prefix local http://www.michaelpjones.co.uk/pipeline/SlipStream_level-0.0.1-py${pyVer}.egg

easy_install --prefix local /home/mike/projects/pipeline/modular/foundation/dist/SlipStream_foundation-0.0.1-py${pyVer}.egg
easy_install --prefix local /home/mike/projects/pipeline/modular/pipeline/dist/SlipStream-0.0.1-py${pyVer}.egg

easy_install --prefix local /home/mike/projects/pipeline/modular/modules/level/dist/SlipStream_level-0.0.1-py${pyVer}.egg

set id=`date "+%Y%m%d-%H%M%S"`
set root="root-$id"
echo local/bin/create_pipeline $root
/tmp/local/bin/create_pipeline $root

setenv PL_LAST_FILE "/tmp/$root/.last"

cd /tmp/$root/jobs_root
source .pipeline_setup

cd /tmp/$root/jobs_root
cd prod/pipeline/scripts

echo "Running Install"
./setup.py install

jr

