import amsoil.core.pluginmanager as pm
import omemberauthorityexceptions

from omemberauthorityresourcemanager import OMemberAuthorityResourceManager

def setup():
    ma_rm = OMemberAuthorityResourceManager()
    pm.registerService('omemberauthorityrm', ma_rm)
    pm.registerService('omemberauthorityexceptions', omemberauthorityexceptions)