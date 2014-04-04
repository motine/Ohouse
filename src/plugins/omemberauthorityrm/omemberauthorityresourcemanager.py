import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('omemberauthorityrm')

import hashlib

from omemberauthorityexceptions import *

class OMemberAuthorityResourceManager(object):
    """
    Manage Member Authority objects and resources.

    Generates neccessary fields when creating a new object.
    """

    AUTHORITY_NAME = 'ma' #: The short-name for this authority

    SUPPORTED_SERVICES = ['MEMBER', 'KEY'] #: The objects supported by this authority

    SUPPORTED_CREDENTIAL_TYPES = [{"type" : "SFA", "version" : 1}] #: The credential type supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Set unique keys.
        """
        super(OMemberAuthorityResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        self._set_unique_keys()

    def _set_unique_keys(self):
        """
        Set the required unique keys in the database for a Member Authority.
        """
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'MEMBER_UID')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'MEMBER_URN')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'KEY_ID')

    #--- 'get_version' methods
    def urn(self):
        """
        Get the URN for this Member Authority.

        Retrieve the hostname from the Flask AMsoil plugin and use this to build
        the URN.

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        return 'urn:publicid:IDN+' + hostname + '+authority+ma'

    def implementation(self):
        """
        Get the implementation details for this Member Authority.

        Retrieve details from the AMsoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('omemberauthorityrm')
        if len(manifest) > 0:
            return {'code_version' : str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Member Authority.
        """
        return self.SUPPORTED_SERVICES

    def api_versions(self):
        """
        Get the different endpoints (of type 'ma'), registered with AMsoil.

        Form these endpoints into a dictionary suitable for the API call response.

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        port = str(config.get('flask.app_port'))
        endpoints = pm.getService('apitools').get_endpoints(type=self.AUTHORITY_NAME)
        return self._resource_manager_tools.form_api_versions(hostname, port,
            endpoints)

    def credential_types(self):
        """
        Return the credential types implemented by this Member Authority.
        """
        return self.SUPPORTED_CREDENTIAL_TYPES

    def fields(self):
        """
        Return the combined supplementary fields applicable to this Member Authority.
        """
        return self._resource_manager_tools.supplementary_fields(self.SUPPLEMENTARY_FIELDS)

    #--- object methods
    def update_member(self, urn, client_cert, credentials, fields, options):
        """
        Update a member object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME,
            fields, 'member', {'MEMBER_URN':urn})

    def lookup_member(self, client_cert, credentials, match, filter_, options):
        """
        Lookup an a member(s).
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME,
            'member', match, filter_)

    def create_key(self, client_cert, credentials, fields, options):
        """
        Create a key object.

        Generate fields for a new object:
            * KEY_ID: hash of the existing 'KEY_PUBLIC' value

        """
        fields['KEY_ID'] = hashlib.sha224(fields['KEY_PUBLIC']).hexdigest()
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME,
            fields, 'key')

    def update_key(self, urn, client_cert, credentials, fields, options):
        """
        Update a key object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME,
            fields, 'key', {'KEY_ID':urn})

    def lookup_key(self, client_cert, credentials, match, filter_, options):
        """
        Lookup a key object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME,
            'key', match, filter_)

    def delete_key(self, urn, client_cert, credentials, options):
        """
        Delete a key object.
        """
        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME,
            'key', {'KEY_ID':urn})
