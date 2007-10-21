from pipeline.shell import Shell
import settings

import os 
import stat
import shutil

def make(self, node):
    """
    Generic make method for creating terminal nodes

    Creates the node's path on disk, templates it and
    creates an entry in the node table.
    """

    if node.depth != settings.depth():
        # internal node
        pipeline.report("Error - cannot make non-terminal node")
        return

    # Create node folder on disk
    file_path = node.file_path()
    os.mkdir(file_path)

    # Process template
    self.template(node)

    # Create the node in the database
    node.create()


def template(self, node):
    """
    Generic template method for making the base content
    of terminal nodes and non-terminal "share" folders.
    """

    shell = Shell()

    module_name = self.__class__.__name__.split("Controller")[0].lower()
    template_path = shell.getenv("PIPELINE") + os.sep + "modules" + os.sep + module_name + os.sep + "template"
    destination_path = node.file_path()
    
    if node.depth == settings.depth():
        # Template terminal folder
        template_path += os.sep + "terminal"
    elif node.depth < settings.depth():
        # Template internal folder
        template_path += os.sep + "internal"
        destination_path += os.sep + 'share'
    else:
        pipeline.report("Error - Invalid node depth")

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

    # If parent node has a non-zero id
    if node.parent.id:
        self.template(node.parent)


