import amsoil.core.pluginmanager as pm
import oregistryexceptions
import oregistryutil

from oregistryresourcemanager import ORegistryResourceManager

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("oregistry.config_path", "deploy/config.json", "JSON file with data for CH, SA, MA")
    
    oregistryutil.load_config() # precache config, also tests if the config file is present

    reg_rm = ORegistryResourceManager()
    pm.registerService('oregistryrm', reg_rm)
    pm.registerService('oregistryexceptions', oregistryexceptions)