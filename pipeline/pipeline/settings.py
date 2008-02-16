import ConfigParser
import os

_path = os.path.join(os.environ["PIPELINE"], "pipeline.ini")

_config = ConfigParser.RawConfigParser()
_config.read(_path)

_hierarchy = _config.get('structure', 'hierarchy')
_abbreviations = _config.get('structure', 'abbreviations')

env_prefix = _config.get('naming', 'env_prefix')
table_prefix = _config.get('naming', 'table_prefix')

def hierarchy():
    return _hierarchy.split()

def abbreviations():
    return _abbreviations.split()

def depth():
    return len(_hierarchy.split())


