import amsoil.core.pluginmanager as pm
from fedrpctwo.gregistryvtwo import GRegistryv2Handler, GRegistryv2DelegateBase
from fedrpctwo.gmavtwo import GMAv2Handler, GMAv2DelegateBase
from fedrpctwo.gsavtwo import GSAv2Handler, GSAv2DelegateBase

def setup():

    xmlrpc = pm.getService('xmlrpc')
    api_tools = pm.getService('apitools')

    greg_handler = GRegistryv2Handler()
    pm.registerService('gregistryv2handler', greg_handler)
    pm.registerService('gregistryv2delegatebase', GRegistryv2DelegateBase)
    xmlrpc.registerXMLRPC('gregv2', greg_handler, '/reg/2') # name, handlerObj, endpoint
    api_tools.register_endpoint(name='gregv2', type='reg', version='2', url='/reg/2')

    gma_handler = GMAv2Handler()
    pm.registerService('gmav2handler', gma_handler)
    pm.registerService('gmav2delegatebase', GMAv2DelegateBase)
    xmlrpc.registerXMLRPC('gmav2', gma_handler, '/ma/2') # name, handlerObj, endpoint
    api_tools.register_endpoint(name='gmav2', type='ma', version='2', url='/ma/2')

    gsa_handler = GSAv2Handler()
    pm.registerService('gsav2handler', gsa_handler)
    pm.registerService('gsav2delegatebase', GSAv2DelegateBase)
    xmlrpc.registerXMLRPC('gsav2', gsa_handler, '/sa/2') # name, handlerObj, endpoint
    api_tools.register_endpoint(name='gsav2', type='sa', version='2', url='/sa/2')
