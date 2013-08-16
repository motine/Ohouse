import amsoil.core.pluginmanager as pm
from ochonedelegate import OCH1Delegate
from omaonedelegate import OMA1Delegate

def setup():
    delegate = OCH1Delegate()
    handler = pm.getService('gchv1handler')
    handler.setDelegate(delegate)
