import ConfigParser
import yaml
import os

_path = os.path.join(os.environ["PIPELINE"], "settings.yaml")

_config_file = open(_path)
_config = yaml.load(_config_file)
_config_file.close()

env_prefix = _config["pipeline"]["naming"]["env_prefix"]
table_prefix = _config["pipeline"]["naming"]["table_prefix"]

def hierarchy():
    return _config["level"]["hierarchy"].split()

def abbreviations():
    return _config["level"]["abbreviations"].split()

def depth():
    return len(_config["level"]["hierarchy"])


