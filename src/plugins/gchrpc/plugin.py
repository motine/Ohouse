import amsoil.core.pluginmanager as pm
from gch1rpc.gchvone import GCHv1Handler, GCHv1DelegateBase
from gch1rpc.gmavone import GMAv1Handler, GMAv1DelegateBase
from gch1rpc import exceptions as gch_exceptions

def setup():
    pm.registerService('gchv1exceptions', gch_exceptions)

    xmlrpc = pm.getService('xmlrpc')

    gch_handler = GCHv1Handler()
    pm.registerService('gchv1handler', gch_handler)
    pm.registerService('gchv1delegatebase', GCHv1DelegateBase)
    xmlrpc.registerXMLRPC('gch', gch_handler, '/CH') # name, handlerObj, endpoint

    gma_handler = GMAv1Handler()
    pm.registerService('gmav1handler', gma_handler)
    pm.registerService('gmav1delegatebase', GMAv1DelegateBase)
    xmlrpc.registerXMLRPC('gma', gma_handler, '/MA') # name, handlerObj, endpoint
