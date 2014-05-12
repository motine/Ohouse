"""
This file contains the bare minimum for bootstrapping AMsoil.
All (non core) implementations/plugins should use the config service/plugin.
"""

import logging
import os.path
import json

from amsoil.core.exception import *


##Paths
SRC_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
ROOT_PATH = os.path.normpath(os.path.join(SRC_PATH, '..'))
PLUGINS_PATH = os.path.join(SRC_PATH, 'plugins')

##Logging
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s [%(levelname)s] - %(message)s"
LOG_FILE = "%s/log/amsoil.log" % (ROOT_PATH,)

##CONFIGDB
CONFIGDB_PATH = "%s/deploy/config.db" % (ROOT_PATH,)
CONFIGDB_ENGINE = "sqlite:///%s" % (CONFIGDB_PATH,)
IS_MULTIPROCESS = True

#CONFIG Details FOR MongoDB


##IPC related parameters
#IPC_RABBITMQ_SERVER="localhost"
# IPC_RABBITMQ_SERVER="192.168.0.218"
##IPC: uncomment to use user/password
#IPC_RABBITMQ_USERNAME="user"
#IPC_RABBITMQ_PASSWORD="pass"


def expand_amsoil_path(path):
    """If the given path is relative, the path will be made absolute, starting from AMsoil's root."""
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return path
    else:
        return os.path.normpath(os.path.join(ROOT_PATH, path))


MONGO_CONFIG_PATH = expand_amsoil_path('deploy/config.json')
try:
    MONGO_CONFIG = json.load(open(MONGO_CONFIG_PATH))
except Exception:
    raise  MissingFileOrData(MONGO_CONFIG_PATH)


default_ip, default_port, default_name= 'localhost', '27017', 'ohouse'
db_ip = MONGO_CONFIG['DATABASE']['server'] or default_ip
db_port = int(MONGO_CONFIG['DATABASE']['port']) or default_port
db_name = MONGO_CONFIG['DATABASE']['name'] or default_name