"""
Please see the documentation in FlaskXMLRPC.
"""
import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('flaskrpcs')

from flaskxmlrpc import FlaskXMLRPC
from flaskserver import FlaskServer

def setup():
    config = pm.getService("config")
    # create default configurations (if they are not already in the database)
    config.install("flask.bind", "0.0.0.0", "IP to bind the Flask RPC to.")
    config.install("flask.port", 9001, "Port to bind the Flask RPC to.")
    config.install("flask.debug", True, "Write logging messages for the Flask RPC server.")
    config.install("flask.wsgi", False, "Use WSGI server instead of the development server.")
    # acquire configuration keys
    cBind = config.get("flask.bind")
    cPort = config.get("flask.port")

    # create and register the RPC server
    flaskserver = FlaskServer(cBind, cPort)
    pm.registerService('rpcserver', flaskserver)
    logger.info("registering rpc server at %s:%i", cBind, cPort)

    # create and register the XML-RPC server
    xmlrpc = FlaskXMLRPC(flaskserver)
    pm.registerService('xmlrpc', xmlrpc)

    # TODO create and register the JSON-RPC server