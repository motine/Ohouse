import amsoil.core.pluginmanager as pm
from g2rpc.genivtworpc import GENIv2RPC

def setup():
    # setup config keys
    config = pm.getService("config")
    # config.Config.install("geniv2rpc.cert_root", "~/.gcf/trusted_roots", "Folder which includes trusted clearinghouse certificates for GENI API v2 (in .pem format)")
    # register xmlrpc endpoint
    xmlrpc = pm.getService('xmlrpc')
    xmlrpc.registerXMLRPC('geni2', GENIv2RPC(), '/RPC2') # name, handlerObj, endpoint
