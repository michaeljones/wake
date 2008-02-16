from mako.template import Template
from pipeline.shell import Shell, EnvVarNotFound

import os
import sys
import pkg_resources

class FakeRequestObject(object):

     def __init__(self):
         pass

     def write(self, value, length=0):
         sys.stderr.write(value)

class View(object):

    def __init__(self):
        pass

    def execute(self, method_name, module_name, vars, req=FakeRequestObject()):

        shell = Shell()
        filename = os.path.join(pkg_resources.resource_filename(module_name, 'view'), "%s.pt" % method_name)

        try:
            mytemplate = Template(filename=filename)
        except IOError:
            return 

        sys.stderr.write(mytemplate.render(**vars))

    def process_file(self, filepath, vars, req=FakeRequestObject()):

        vars['req'] = req

        try:
            source = _psp.parse(filepath)
        except IOError:
            return

        code = compile(source, filepath, "exec")

        global_scope = globals().copy()
        global_scope.update(vars)

        exec code in global_scope




