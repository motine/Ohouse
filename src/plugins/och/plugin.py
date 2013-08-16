import amsoil.core.pluginmanager as pm
from ochonedelegate import OCH1Delegate
from omaonedelegate import OMA1Delegate

def setup():
    ch_delegate = OCH1Delegate()
    ch_handler = pm.getService('gchv1handler')
    ch_handler.setDelegate(ch_delegate)

    ma_delegate = OMA1Delegate()
    ma_handler = pm.getService('gmav1handler')
    ma_handler.setDelegate(ma_delegate)