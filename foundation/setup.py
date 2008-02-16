from setuptools import setup, find_packages

setup(
    name = "SlipStream-foundation",
    version = "0.0.1",
    packages = find_packages(),
    install_requires = ['SQLAlchemy>=0.4', 'Mako>=0.1.10'],

    # metadata for upload to PyPI
    author = "Michael Jones",
    author_email = "m.pricejones@gmail.com",
    description = "Foundation package for pipeline",
    keywords = "animation pipeline workflow project",
    url = "http://www.michaelpjones.co.uk/pipeline/trac",   # project home page, if any

)



