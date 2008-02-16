from optparse import OptionParser

import sys
import os
import pkg_resources
import shutil
import pipeline

def main():
    
    parser = OptionParser()

    opts, args = parser.parse_args()

    root = args[0]

    # Directory creation
    # jobs_root = os.path.join(root, "jobs_root")
    # data_root = os.path.join(root, "data_root")

    # prod = os.path.join(jobs_root, "prod")
    # pipeline = os.path.join(prod, "pipeline")

    # os.makedirs(pipeline)
    # os.makedirs(data_root)

    # pipeline_dirs = ["bin", "modules", "db"]

    # for dir in pipeline_dirs:
    #     path = os.path.join(pipeline, dir)
    #     os.makedirs(path)

    template = os.path.join(pipeline.etc(), "empty")

    shutil.copytree(template, root)

    os.makedirs(os.path.join(root, "data_root"))
    pl_path = os.path.join(root, "jobs_root", "prod", "pipeline")
    os.makedirs(os.path.join(pl_path, "bin"))
    os.makedirs(os.path.join(pl_path, "db"))
    os.makedirs(os.path.join(pl_path, "modules", "resources"))

    # etc/empty
    # etc/empty/jobs_root
    # etc/empty/data_root
    # etc/empty/jobs_root/prod
    # etc/empty/jobs_root/.pipeline_setup
    # etc/empty/jobs_root/prod/pipeline
    # etc/empty/jobs_root/prod/pipeline/scripts
    # etc/empty/jobs_root/prod/pipeline/bin
    # etc/empty/jobs_root/prod/pipeline/db
    # etc/empty/jobs_root/prod/pipeline/modules
    # etc/empty/jobs_root/prod/pipeline/pipeline.ini
    # etc/empty/jobs_root/prod/pipeline/scripts/dispatch.py
    # etc/empty/jobs_root/prod/pipeline/scripts/setup.py
    # etc/empty/jobs_root/prod/pipeline/scripts/dispatch.sh
    # etc/empty/jobs_root/prod/pipeline/modules/resources




    # Setup script
    
    

