from pipeline.controller.base import ModuleController, FailedRequest
from node.model import Node, InvalidLevel, PathError

import pipeline 
import settings
from pipeline.shell import Shell, EnvVarNotFound

import sys
import shutil
import os

class NodeController(ModuleController):
    """ Controller for the node module. """

    allow_invalid_node_for = ["make"]
    scaffold = ['template']

    def get_node(self, method_name):
        level = self.args[0]
        syntax = self.args[1]

        depth = None
        try:
            depth = Node.depth(level)
        except InvalidLevel, e:
            pipeline.report("Error - Invalid pipeline level: " + str(e))
            raise FailedRequest

        try: 
            syntax = Node.complete_syntax(syntax, depth)
        except PathError:
            pipeline.report("Error - Unable to complete path from environment.")
            raise FailedRequest 

        node = Node.find_by_syntax(syntax, strict=False)

        if method_name not in self.allow_invalid_node_for: 
            if not node:
                pipeline.report("Error - Node \"" + syntax + "\" does not exist")
                raise FailedRequest

        return node

    def write_last(self, node):

        # Write information out to .last file in users HOME
        # Only if it is different to the current one
        last_file = os.getenv("HOME") + os.sep + ".last"
        old_syntax = ""
        try:
            last = open(last_file, "r")
            old_syntax = last.readline()
            last.close()
        except IOError:
            pass

        # If new is different to old then write it out
        new_syntax = node.syntax()
        if new_syntax != old_syntax:
            last = open(last_file, "w")
            last.write(node.syntax())
            last.close()



    def make(self):
        """
        This method is responsible for:
            - Creating the node folder
            - Creating the "share" folder
            - Templating the share folder
            - Entering the node into the database

        It will exit if the node already exists or if the 
        path is in some way invalid.
        """

        node = self.get_node("make")

        if node:
            pipeline.report("Error - Node already exists - " + str(node))
            return

        if not node.parent: 
            pipeline.report("Error - Invalid path")
            return

        # Create node folder on disk
        file_path = node.file_path()
        os.mkdir(file_path)

        # Create the share folder 
        os.mkdir(file_path + os.sep + "share")

        # Process template
        self.template(node)

        # Create the node in the database
        node.create()

        # Set up the environment for the node
        self.set()


    def remove(self):
        """
        Removes the node and all it's children from 
        the filesystem and the database.
        """

        node = self.get_node("remove")

        levels = settings.hierarchy()
        abbr = settings.abbreviations()

        aliases = ['', 'bin']

        shell = Shell()

        # If we're removing a node in our current environment
        clean_env = True
        for n in node.branch():
            # Check each level of the env against our node branch
            clean_env = True
            try:
                clean_env = (n.name != shell.getenv("@" + levels[n.depth].upper()))
            except EnvVarNotFound:
                clean_env = False
                break

            # Necessary?
            if not clean_env:
                break

        # If necessary unset all environment variables and aliases
        # associated with this level and those below
        if clean_env:
            depth = node.depth
            for level in levels[node.depth:]:
                shell.unset("@" + level.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1


        # Write out a syntax file so it is up-to-date with current env
        self.write_last(node.parent)

        shell.commit()

        # Remove the node from disk
        shutil.rmtree(node.file_path())

        # Remove the node and all its children from the database
        node.destroy_subtree()


    def set(self):
        """ 
        Sets the environment to correspond to this node.
        """
        
        node = self.get_node("remove")

        shell = Shell()

        levels = settings.hierarchy()
        abbr = settings.abbreviations()

        pattern = shell.getenv("@JOBS_ROOT") + r'/[\w/]*/share/bin'
        shell.clean('PATH', pattern)

        pattern = shell.getenv("@JOBS_ROOT") + r'/prod/[\w/]*'
        shell.clean('PATH', pattern)

        aliases = ['', 'bin']

        # Remove all environment variables and aliases
        # associated with levels below this one
        depth = node.depth + 1
        if node.depth < len(levels) - 1:
            for level in levels[node.depth + 1:]:
                shell.unset("@" + level.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1
                

        bin_path = ""
        # Set environment from node 
        for n in node.branch():
            shell.set("@" + levels[n.depth], n.name)
            bin_path += "%s/share/bin:" % n.file_path()

        # Set aliases
        cd_path = "cd $@JOBS_ROOT"
        for index, level in enumerate(levels[:node.depth + 1]):
            # alias current level
            cd_path += os.sep + "$@" + level.upper()
            shell.alias(abbr[index], cd_path)

        prod = shell.getenv("@PROD")
        bin_path += "%s/bin" % prod
        shell.insert("PATH", bin_path)

        self.write_last(node)

        shell.commit()


