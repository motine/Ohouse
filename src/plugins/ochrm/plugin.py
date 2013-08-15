import amsoil.core.pluginmanager as pm
import ochexceptions
import ochutil

from ochrmch import OCHResourceManager

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("och.config_path", "deploy/config.json", "JSON file with data for CH, SA, MA")
    
    ochutil.load_config() # precache config, also tests if the config file is present

    ch_rm = OCHResourceManager()
    pm.registerService('ochrm', ch_rm)
    pm.registerService('ochexceptions', ochexceptions)