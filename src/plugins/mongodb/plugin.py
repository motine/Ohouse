import amsoil.core.pluginmanager as pm
from mongodatabase import MongoDB

def setup():
    mongo_database = MongoDB()
    pm.registerService('mongodb', mongo_database)