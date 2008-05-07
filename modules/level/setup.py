from setuptools import setup, find_packages

import os

def package_data():

    data = [] 
    top = os.path.join(os.getcwd(), "level", "etc")
    remove = os.path.join(os.getcwd(), "level", "")

    for root, dirs, files in os.walk(top, topdown=True):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            dir_path = dir_path.replace(remove, "")
            # print dir_path
            # data.append(dir_path)

        for name in files:
            if not name.endswith("~"):
                path = os.path.join(root, name)
                path = path.replace(remove, "")
                data.append(path)

    top = os.path.join(os.getcwd(), "level", "view")
    remove = os.path.join(os.getcwd(), "level", "")

    for root, dirs, files in os.walk(top, topdown=True):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            dir_path = dir_path.replace(remove, "")
            # print dir_path
            # data.append(dir_path)

        for name in files:
            if not name.endswith("~"):
                path = os.path.join(root, name)
                path = path.replace(remove, "")
                data.append(path)

    return data


setup(
    name = "wake-level",
    version = "0.0.1",
    packages = find_packages(),
    install_requires = ['wake>=0.0.1'],

    entry_points = {
        'pipeline.module.setup': 'level = level.setup:setup',
        'pipeline.module.install': 'level = level.setup:install',
    },

    package_data = {
        '' : package_data() 
    },

    # metadata for upload to PyPI
    author = "Michael Jones",
    author_email = "m.pricejones@gmail.com",
    description = "The level module for the pipeline",
    keywords = "animation pipeline workflow project",
    url = "http://www.michaelpjones.co.uk/pipeline/trac",   
)

