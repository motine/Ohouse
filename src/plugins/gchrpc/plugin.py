import amsoil.core.pluginmanager as pm
from gch1rpc.gchvone import GCHv1Handler, GCHv1DelegateBase
from gch1rpc import exceptions as gch_exceptions

def setup():
    xmlrpc = pm.getService('xmlrpc')
    gch_handler = GCHv1Handler()
    pm.registerService('gchv1handler', gch_handler)
    pm.registerService('gchv1delegatebase', GCHv1DelegateBase)
    pm.registerService('gchv1exceptions', gch_exceptions)
    xmlrpc.registerXMLRPC('gch', gch_handler, '/CH') # name, handlerObj, endpoint
