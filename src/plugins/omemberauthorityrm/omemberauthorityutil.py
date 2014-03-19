import amsoil.core.pluginmanager as pm
from amsoil.config import expand_amsoil_path

import omemberauthorityexceptions

def form_api_versions(hostname, port, endpoints):
    api_versions = {}
    for key, endpoint in endpoints.iteritems():
        api_versions[endpoint.get('version')] = 'https://' + hostname + ':' + port + endpoint.get('url')
    return api_versions