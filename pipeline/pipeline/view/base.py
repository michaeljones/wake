from mako.template import Template
from pipeline.shell import Shell, EnvVarNotFound

import os
import sys
import pkg_resources

class View(object):

    def __init__(self):
        pass

    def execute(self, method_name, module_name, vars):

        shell = Shell()
        filename = os.path.join(pkg_resources.resource_filename(module_name, 'view'), "%s.pt" % method_name)

        try:
            mytemplate = Template(filename=filename)
        except IOError:
            return 

        sys.stderr.write(mytemplate.render(**vars))


