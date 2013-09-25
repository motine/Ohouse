import amsoil.core.pluginmanager as pm
from gfed1rpc.gregistryvone import GRegv1Handler, GRegv1DelegateBase
from gfed1rpc.gmavone import GMAv1Handler, GMAv1DelegateBase
from gfed1rpc import exceptions as gfed_exceptions

def setup():
    pm.registerService('gfedv1exceptions', gfed_exceptions)

    xmlrpc = pm.getService('xmlrpc')

    greg_handler = GRegv1Handler()
    pm.registerService('gregistryv1handler', greg_handler)
    pm.registerService('gregistryv1delegatebase', GRegv1DelegateBase)
    xmlrpc.registerXMLRPC('greg', greg_handler, '/REG') # name, handlerObj, endpoint

    gma_handler = GMAv1Handler()
    pm.registerService('gmav1handler', gma_handler)
    pm.registerService('gmav1delegatebase', GMAv1DelegateBase)
    xmlrpc.registerXMLRPC('gma', gma_handler, '/MA') # name, handlerObj, endpoint
