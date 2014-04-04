import amsoil.core.pluginmanager as pm
import oregistryexceptions

from oregistryresourcemanager import ORegistryResourceManager

def setup():
    reg_rm = ORegistryResourceManager()
    pm.registerService('oregistryrm', reg_rm)
    pm.registerService('oregistryexceptions', oregistryexceptions)
