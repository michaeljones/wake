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

    def get_levels(self, method_name, strict=False):

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

        levels = Level.link(levels)

        # Check for + signs
        segments = syntax.split(":")

        if not strict:
            for index, level in enumerate(levels):
                if level.depth < depth:
                    last = level
                    for d in range(level.depth + 1, depth + 1):
                        new_record = { "name" : segments[d],
                                       "depth" : d,
                                       "parent_id" : last.id }

                        parent = last
                        last = Level(new_record)
                        last.parent = parent
                        levels[index] = last

        if not levels:
            new_record = { "name" : syntax,
                           "depth" : 0, 
                           "parent_id" : 0 }

            # Create a level 
            level = Level(new_record)

            # Give it production level parent
            level.parent =  Level({"name" : "", "id" : 0, "parent" : None })
            level.parent_id = 0

            levels.append(level)

        if method_name not in self.allow_invalid_level_for:
            for level in levels:
                if not level:
                    pipeline.report("Error - Level \"" + level.syntax() + "\" does not exist")
                    raise FailedRequest

        return levels


    #
    #   Methods
    #

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

        levels = self.get_levels("make")

        if len(levels) > 1:
            pipeline.report("Error - Syntax matches one or more existing levels") 
            return

        if levels and levels[0]:
            pipeline.report("Error - Level already exists - " + str(levels[0]))
            return

        level = levels[0]

        error = False
        try:
            if not level.parent: 
                error = True
        except AttributeError:
            error = True
        finally:
            if error:
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

        levels = self.get_levels("remove")

        if not levels:
            pipeline.report("Error - Syntax does not match any levels")
            return

        if len(levels) > 1:
            pipeline.report("Error - Syntax matches multiple levels")
            return

        level = levels[0]

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
        
        levels = self.get_levels("set")

        if not levels:
            pipeline.report("Error - Syntax does not match any levels")
            return

        if len(levels) > 1:
            pipeline.report("Error - Syntax matches multiple levels")
            return

        level = levels[0]

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

        levels = self.get_levels("list", True)
        
        # TODO: Add option for printing complete paths

        self.view.title = "List Method"
        self.view.levels = levels

        return

        for level in levels:

            sys.stderr.write(str(level.syntax()) + "\n")


    def status(self):

        shell = Shell()

        path = ""
        joiner = ""

        for index, level_name in enumerate(settings.hierarchy()):
            try:
                path += joiner + shell.getenv("@" + level_name.upper())
            except EnvVarNotFound:
                continue

            joiner = ":"

        sys.stderr.write("%s\n" % path)




    #
    #   Utilities
    #

    def write_last(self, level):

        # Write information out to .last file in users HOME
        # Only if it is different to the current one
        # FIXME: Should use shell object
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




