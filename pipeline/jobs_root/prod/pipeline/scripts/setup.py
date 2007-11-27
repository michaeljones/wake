#!/usr/bin/python -tt

import os
import sys

from optparse import OptionParser

def environment():
    """
    Configures all non-module-specific environment
    information for the pipeline.

    Calls the appropriate environment method for each installed
    module.
    """

    
    # Assume this is being run in the jobs_root directory
    jobs_root = os.getcwd()
    data_root = os.path.join(os.path.dirname(jobs_root), "data_root")

    prod = os.path.join(jobs_root, "prod")
    pipeline = os.path.join(prod, "pipeline")

    pipeline_lib = os.path.join(pipeline, "lib")
    pipeline_modules = os.path.join(pipeline, "modules")

    man_path = os.path.join(pipeline, "man")

    sys.path.insert(0, pipeline_modules)
    sys.path.insert(0, pipeline_lib)


    # Prep shell object
    pipeline_module = __import__("pipeline.shell", globals(), locals(), [None])
    Shell = getattr(pipeline_module, "Shell")

    shell = Shell()

    # Set up environment using shell object
    #
    # Set general pipeline environment
    shell.set("@JOBS_ROOT", jobs_root)
    shell.set("@DATA_ROOT", data_root)

    shell.set("@PROD", prod)

    # Special variable
    shell.set("PIPELINE", pipeline)

    # System paths
    shell.insert("PYTHONPATH", pipeline_modules)
    shell.insert("PYTHONPATH", pipeline_lib)
    shell.insert("MANPATH", man_path)

    # Invent some cunning and unobtrusive way of 
    # automagically inserting the right prefix into 
    # the environment variables. 
    shell.alias("jr", "cd $@JOBS_ROOT")
    shell.alias("dr", "cd $@DATA_ROOT")
    shell.alias("prod", "cd $@PROD")

    # Get specific environment from each module
    modules = os.listdir(pipeline_modules)

    for module in modules:
        if not module.startswith("."):
            try:
                env_module = __import__(module+".setup", globals(), locals(), [None])
            except ImportError:
                sys.stderr.write("Error - Failed to import module " + module + "\n")
                continue

            setup = getattr(env_module, "setup")
            setup(shell)

    # Commit changes
    shell.commit()

def install():
    """
    Calls install on each module in the pipeline/modules
    directory.
    """

    # Designed to be run from the pipeline/scripts folder
    pipeline = os.path.split(os.getcwd())[0]

    pipeline_lib = os.path.join(pipeline, "lib")
    pipeline_modules = os.path.join(pipeline, "modules")

    sys.path.insert(0, pipeline_modules)
    sys.path.insert(0, pipeline_lib)

    # Check settings
    settings = __import__("settings", globals(), locals(), [None])

    print "Validating settings."
    if len(settings.hierarchy()) != len(settings.abbreviations()):
        pipeline.report("Error - abbreviation list does not have a 1-to-1 relationship with the hierarchy.")
        return

    print "Settings valid."

    modules = os.listdir(pipeline_modules)

    for module in modules:
        if not module.startswith("."):
            try:
                env_module = __import__(module+".setup", globals(), locals(), [None])
            except ImportError:
                continue

            install = getattr(env_module, "install")
            install()


    print "Installation complete."


def main():
    """
    Runs the appropriate method according to the 
    commandline argument provided.
    """

    parser = OptionParser()

    opt, args = parser.parse_args()

    method = {}
    method["install"] = install
    method["environment"] = environment

    method[args[0]]()

if __name__ == "__main__":
    main()


