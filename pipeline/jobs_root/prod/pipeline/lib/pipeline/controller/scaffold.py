from pipeline.shell import Shell
import settings

import os 
import stat
import shutil

def make(self, level):
    """
    Generic make method for creating terminal levels

    Creates the level's path on disk, templates it and
    creates an entry in the level table.
    """

    if level.depth != settings.depth():
        # internal level
        pipeline.report("Error - cannot make non-terminal level")
        return

    # Create level folder on disk
    file_path = level.file_path()
    os.mkdir(file_path)

    # Process template
    self.template(level)

    # Create the level in the database
    level.create()


def template(self, level):
    """
    Generic template method for making the base content
    of terminal levels and non-terminal "share" folders.
    """

    shell = Shell()

    module_name = self.__class__.__name__.split("Controller")[0].lower()
    template_path = shell.getenv("PIPELINE") + os.sep + "modules" + os.sep + module_name + os.sep + "template"
    destination_path = level.file_path()
    
    if level.depth == settings.depth():
        # Template terminal folder
        template_path += os.sep + "terminal"
    elif level.depth < settings.depth():
        # Template internal folder
        template_path += os.sep + "internal"
        destination_path += os.sep + 'share'
    else:
        pipeline.report("Error - Invalid level depth")

    contents = os.listdir(template_path)

    for item in contents:

        item_source = template_path + os.sep + item
        item_destination = os.path.join(destination_path, item)

        if not os.path.exists(item_destination):
            mode = os.stat(item_source)[stat.ST_MODE]
            if stat.S_ISDIR(mode):
                shutil.copytree(item_source, item_destination)
            else:
                shutil.copy(item_source, item_destination)

    # If parent level has a non-zero id
    if level.parent.id:
        self.template(level.parent)


