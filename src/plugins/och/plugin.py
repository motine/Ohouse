import amsoil.core.pluginmanager as pm
from ochonedelegate import OCH1Delegate
from omaonedelegateguard import OMA1DelegateGuard

"""
The delegate concept (introduced by AMsoil) was extended here.
Now there is the delegate which does the actual work (either itself or delegates to a Resource Manager).
The delegate may be wrapped in a guard.
This guard derives from the original delegate and checks the incoming/outgoing values with respect to authorization.
E.g. The orginal delegate would deliver private information to the user becuase it is not concerned with authorization.
The guard on the other hand checks the outgoing result and raises an exception if the user does not have the right privileges.
"""

def setup():
    config = pm.getService('config')
    config.install("och.cert_root", "deploy/trusted", "Folder which includes trusted certificates (in .pem format). If relative path, the root is assumed to be git repo root.")
    
    ch_delegate = OCH1Delegate()
    ch_handler = pm.getService('gchv1handler')
    ch_handler.setDelegate(ch_delegate)

    ma_delegate = OMA1DelegateGuard()
    ma_handler = pm.getService('gmav1handler')
    ma_handler.setDelegate(ma_delegate)