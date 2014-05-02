import amsoil.core.pluginmanager as pm
from resourcemanagertools import ResourceManagerTools
from delegatetools import DelegateTools
from apitools import APITools
import apiexceptionsv1, apiexceptionsv2

def setup():

    pm.registerService('apiexceptionsv1', apiexceptionsv1)
    pm.registerService('apiexceptionsv2', apiexceptionsv2)

    api_tools = APITools()
    pm.registerService('apitools', api_tools)

    resource_manager_tools = ResourceManagerTools()
    pm.registerService('resourcemanagertools', resource_manager_tools)

    config = pm.getService("config")
    config.install("delegatetools.config_path", "deploy/config.json", "JSON file with configuration data for CH, SA, MA")
    config.install("delegatetools.defaults_path", "src/plugins/fedtools/defaults.json", "JSON file with default data for CH, SA, MA", True)

    delegate_tools = DelegateTools()
    pm.registerService('delegatetools', delegate_tools)

