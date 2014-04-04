import amsoil.core.pluginmanager as pm
from resourcemanagertools import ResourceManagerTools
from delegatetools import DelegateTools
from apitools import APITools
import apiexceptions

def setup():

    pm.registerService('apiexceptions', apiexceptions)

    api_tools = APITools()
    pm.registerService('apitools', api_tools)

    resource_manager_tools = ResourceManagerTools()
    pm.registerService('resourcemanagertools', resource_manager_tools)

    config = pm.getService("config")
    config.install("delegatetools.config_path", "deploy/config.json", "JSON file with configuration data for CH, SA, MA")
    config.install("delegatetools.defaults_path", "deploy/defaults.json", "JSON file with default data for CH, SA, MA")

    delegate_tools = DelegateTools()
    pm.registerService('delegatetools', delegate_tools)

