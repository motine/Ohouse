import os.path
import json

import amsoil.core.pluginmanager as pm
from amsoil.config import expand_amsoil_path

import oregistryexceptions

CONFIG = None

def config_path():
    config = pm.getService("config")
    path = config.get("oregistry.config_path") # this could be cached
    return expand_amsoil_path(path)

def strip_comments(json):
    JSON_COMMENT = "__comment"
    if type(json) in [str, unicode, int, float, bool, type(None)]: # atomic element
        return json
    if isinstance(json, list):
        return [strip_comments(j) for j in json if not ((type(j) in [str, unicode]) and j.startswith(JSON_COMMENT))]
    if isinstance(json, dict):
        return dict( (k, strip_comments(v)) for (k,v) in json.iteritems() if k != JSON_COMMENT) # there would be a dict comprehension from 2.7

def load_config():
    """Caches the config and makes it available in this package (as static variable)"""
    path = config_path()
    if not os.path.exists(path):
        raise oregistryexceptions.RegistryConfigFileMissing(path)
    try:
        config = json.load(open(path))
    except:
        raise oregistryexceptions.RegistryMalformedConfigFile(path, '')
    global CONFIG
    CONFIG = strip_comments(config)