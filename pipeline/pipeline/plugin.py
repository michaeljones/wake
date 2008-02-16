# Plugin access using setuptools/pkg_resources
# File is modelled after the approach in pygments

try:
    import pkg_resources
except ImportError:
    pkg_resources = None

MODULE_SETUP_ENTRY_POINT = 'pipeline.module.setup'
MODULE_INSTALL_ENTRY_POINT = 'pipeline.module.install'

def find_plugin_module_setups():
    if pkg_resources is None:
        return
    for entrypoint in pkg_resources.iter_entry_points(MODULE_SETUP_ENTRY_POINT):
        yield entrypoint.load()


def find_plugin_module_installs():
    if pkg_resources is None:
        return
    for entrypoint in pkg_resources.iter_entry_points(MODULE_INSTALL_ENTRY_POINT):
        yield entrypoint.load()



