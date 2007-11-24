from pipeline.controller.base import ModuleController, FailedRequest
from level.model import Level, InvalidLevel, PathError

import pipeline 
import settings
from pipeline.shell import Shell, EnvVarNotFound

import sys
import shutil
import os

class LevelController(ModuleController):
    """ Controller for the level module. """

    allow_invalid_level_for = ["make"]
    scaffold = ['template']

    def get_level(self, method_name):
        level_name = self.args[0]
        syntax = self.args[1]

        depth = None
        try:
            depth = Level.depth(level_name)
        except InvalidLevel, e:
            pipeline.report("Error - Invalid pipeline level: " + str(e))
            raise FailedRequest

        try: 
            syntax = Level.complete_syntax(syntax, depth)
        except PathError:
            pipeline.report("Error - Unable to complete path from environment.")
            raise FailedRequest 

        levels = Level.find_by_syntax(syntax, strict=False)

        if len(levels) > 1:
            pipeline.report("Error - Syntax matches multiple levels")
            raise FailedRequest

        level = levels[0]

        if method_name not in self.allow_invalid_level_for:
            if not level:
                pipeline.report("Error - Level \"" + syntax + "\" does not exist")
                raise FailedRequest

        return level

    def write_last(self, level):

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
        new_syntax = level.syntax()
        if new_syntax != old_syntax:
            last = open(last_file, "w")
            last.write(level.syntax())
            last.close()


    def make(self):
        """
        This method is responsible for:
            - Creating the level folder
            - Creating the "share" folder
            - Templating the share folder
            - Entering the level into the database

        It will exit if the level already exists or if the 
        path is in some way invalid.
        """

        level = self.get_level("make")

        if level:
            pipeline.report("Error - Level already exists - " + str(level))
            return

        if not level.parent: 
            pipeline.report("Error - Invalid path")
            return

        # Create level folder on disk
        file_path = level.file_path()
        os.mkdir(file_path)

        # Create the share folder 
        os.mkdir(file_path + os.sep + "share")

        # Process template
        self.template(level)

        # Create the level in the database
        level.create()

        # Set up the environment for the level
        self.set()


    def remove(self):
        """
        Removes the level and all it's children from 
        the filesystem and the database.
        """

        level = self.get_level("remove")

        hierarchy = settings.hierarchy()
        abbr = settings.abbreviations()

        aliases = ['', 'bin']

        shell = Shell()

        # If we're removing a level in our current environment
        clean_env = True
        for n in level.branch():
            # Check each level of the env against our level branch
            clean_env = True
            try:
                clean_env = (n.name != shell.getenv("@" + hierarchy[n.depth].upper()))
            except EnvVarNotFound:
                clean_env = False
                break

            # Necessary?
            if not clean_env:
                break

        # If necessary unset all environment variables and aliases
        # associated with this level and those below
        if clean_env:
            depth = level.depth
            for level_name in hierarchy[level.depth:]:
                shell.unset("@" + level_name.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1


        # Write out a syntax file so it is up-to-date with current env
        self.write_last(level.parent)

        shell.commit()

        # Remove the level from disk
        shutil.rmtree(level.file_path())

        # Remove the level and all its children from the database
        level.destroy_subtree()


    def set(self):
        """ 
        Sets the environment to correspond to this level.
        """
        
        level = self.get_level("remove")

        shell = Shell()

        hierarchy = settings.hierarchy()
        abbr = settings.abbreviations()

        pattern = shell.getenv("@JOBS_ROOT") + r'/[\w/]*/share/bin'
        shell.clean('PATH', pattern)

        pattern = shell.getenv("@JOBS_ROOT") + r'/prod/[\w/]*'
        shell.clean('PATH', pattern)

        aliases = ['', 'bin']

        # Remove all environment variables and aliases
        # associated with levels below this one
        depth = level.depth + 1
        if level.depth < len(hierarchy) - 1:
            for level_name in hierarchy[level.depth + 1:]:
                shell.unset("@" + level_name.upper())
                for alias in aliases:
                    shell.unalias(abbr[depth] + alias)

                depth += 1
                

        bin_path = ""
        # Set environment from level 
        for l in level.branch():
            shell.set("@" + hierarchy[l.depth], l.name)
            bin_path += "%s/share/bin:" % l.file_path()

        # Set aliases
        cd_path = "cd $@JOBS_ROOT"
        for index, level_name in enumerate(hierarchy[:level.depth + 1]):
            # alias current level
            cd_path += os.sep + "$@" + level_name.upper()
            shell.alias(abbr[index], cd_path)

        prod = shell.getenv("@PROD")
        bin_path += "%s/bin" % prod
        shell.insert("PATH", bin_path)

        self.write_last(level)

        shell.commit()


    def list(self):

        level_name = self.args[0]
        
        # Find out what depth we're looking at
        depth = None
        try:
            depth = Level.depth(level_name)
        except InvalidLevel, e:
            pipeline.report("Error - Invalid pipeline level: " + str(e))
            raise FailedRequest

        # Get the syntax from the arguments if one is provided
        syntax = ""
        try:
            syntax = self.args[1]
        except IndexError:
            if depth != 0:
                pipeline.report("Error - Must specify path information")

        # Complete it
        try: 
            syntax = Level.complete_syntax(syntax, depth)
        except PathError:
            pipeline.report("Error - Unable to complete path from environment.")
            raise FailedRequest 

        # Remove the last element 
        syntax = ":".join(syntax.split(":")[:-1])
        if syntax:
            syntax += ":+"
        else:
            syntax = "+"

        sys.stderr.write( syntax + "\n" )
        
        # Retrieve the children from the database
        children = Level.find_by_syntax(syntax)
        
        # Print the names of the children
        sys.stderr.write( str(children) + "\n" )

        # TODO: Add option for printing complete paths



