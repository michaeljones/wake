import os
import sys
import shutil

from optparse import OptionParser

def environment():
    """
    Configures all non-module-specific environment
    information for the pipeline.

    Calls the appropriate environment method for each installed
    module.
    """

    from pipeline import plugin
    
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

    # This has to be set in order for "setting.py" to have a reference point
    # for finding the pipeline.ini. It can't rely on Shell class as Shell relies
    # on settings for the env_prefix setting
    os.environ["PIPELINE"] = pipeline

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

    for module_setup in plugin.find_plugin_module_setups():
        # sys.stderr.write(str(module_setup))
        module_setup(shell)

    # Commit changes
    shell.commit()

def install():
    """
    Calls install on each module in the pipeline/modules
    directory.
    """

    from pipeline import plugin

    # Designed to be run from the pipeline/scripts folder
    pipeline = os.path.split(os.getcwd())[0]

    pipeline_lib = os.path.join(pipeline, "lib")
    pipeline_modules = os.path.join(pipeline, "modules")

    sys.path.insert(0, pipeline_modules)
    sys.path.insert(0, pipeline_lib)

    # Check settings
    settings = __import__("pipeline.settings", globals(), locals(), [None])

    print "Validating settings."

    if len(settings.hierarchy()) != len(settings.abbreviations()):
        pipeline.report("Error - abbreviation list does not have a 1-to-1 relationship with the hierarchy.")
        return

    print "Settings valid."

    for module_install in plugin.find_plugin_module_installs():
        # sys.stderr.write(str(module_setup))
        module_install()

    print "Installation complete."


def create():

    import pipeline.utils

    parser = OptionParser()

    opts, args = parser.parse_args()

    root = args[1]

    etc = pipeline.utils.etc()

    template = os.path.join(etc, "structure")

    shutil.copytree(template, root)

    shutil.copyfile(os.path.join(etc, "pipeline_setup"), os.path.join(root, "jobs_root", ".pipeline_setup"))

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

def dispatch():

    from pipeline.dispatch.commandline import CommandlineController

    # As the output of this script is designed to
    # be sourced. Make sure that if nothing else
    # is provided, it at least has a blank line to "run"
    print "echo -n;"

    dispatcher = CommandlineController()
    dispatcher.process_request()

    

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
    method["create"] = create
    method["dispatch"] = dispatch

    method[args[0]]()



