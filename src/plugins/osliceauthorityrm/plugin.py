import amsoil.core.pluginmanager as pm
import osliceauthorityexceptions

from osliceauthorityresourcemanager import OSliceAuthorityResourceManager

def setup():
    sa_rm = OSliceAuthorityResourceManager()
    pm.registerService('osliceauthorityrm', sa_rm)
    pm.registerService('osliceauthorityexceptions', osliceauthorityexceptions)