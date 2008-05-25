from pipeline.controller.base import ModuleController, FailedRequest

from werkzeug import Template

import os
import pkg_resources

class DevelopmentController(ModuleController):
    """ Controller for the development module. """


    def make(self, args):

        self.module_name = args[0]
        self.module_path = self.module_name

        os.makedirs(self.module_name + os.sep + self.module_name)

        self.process_file("setup.wz", "setup.py")
        self.process_file("__init__.wz", "pipeline" + os.sep + "__init__.py")
        self.process_file("module" + os.sep + "__init__.wz", "pipeline" + os.sep + self.module_name + os.sep + "__init__.py")
        self.process_file("module" + os.sep + "controller.wz", "pipeline" + os.sep + self.module_name + os.sep + "controller.py")
        self.process_file("module" + os.sep + "model.wz", "pipeline" + os.sep + self.module_name + os.sep + "model.py")
        self.process_file("module" + os.sep + "setup.wz", "pipeline" + os.sep + self.module_name + os.sep + "setup.py")


    #
    #   Utils
    #
    def process_file(self, source, destination):


        filename = os.path.join(pkg_resources.resource_filename("development", 'etc'), source) 

        template = Template.from_file(filename)

        vars_ = {
                "module" : self.module_name,
                "Module" : self.module_name.capitalize(),
                }

        template.render()

        output = open(os.path.join(self.module_path, destination), "w")
        output.write(template.render(**vars_))
        output.close()


