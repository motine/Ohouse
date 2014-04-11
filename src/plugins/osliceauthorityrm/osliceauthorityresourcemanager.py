import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('osliceauthorityrm')

import uuid
import pyrfc3339
import datetime
import pytz

class OSliceAuthorityResourceManager(object):
    """
    Manage Slice Authority objects and resources.

    Generates neccessary fields when creating a new object.
    """

    AUTHORITY_NAME = 'sa' #: The short-name for this authority

    SUPPORTED_SERVICES = ['SLICE','SLICE_MEMBER', 'SLIVER_INFO', 'PROJECT', 'PROJECT_MEMBER'] #: The objects supported by this authority

    SUPPORTED_CREDENTIAL_TYPES = [{"type" : "SFA", "version" : 1}] #: The credential type supported by this authority

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Set unique keys.
        """
        super(OSliceAuthorityResourceManager, self).__init__()
        self._resource_manager_tools = pm.getService('resourcemanagertools')
        self._set_unique_keys()

    #--- 'get_version' methods
    def _set_unique_keys(self):
        """
        Set the required unique keys in the database for a Slice Authority.
        """
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLICE_UID')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLICE_URN')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'SLIVER_INFO_URN')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'PROJECT_UID')
        self._resource_manager_tools.set_index(self.AUTHORITY_NAME, 'PROJECT_URN')

    def urn(self):
        """
        Get the URN for this Slice Authority.

        Retrieve the hostname from the Flask AMsoil plugin and use this to build
        the URN.

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        return 'urn:publicid:IDN+' + hostname + '+authority+sa'

    def implementation(self):
        """
        Get the implementation details for this Slice Authority.

        Retrieve details from the AMsoil plugin and form them into a dictionary
        suitable for the API call response.

        """
        manifest = pm.getManifest('osliceauthorityrm')
        if len(manifest) > 0:
            return {'code_version' : str(manifest['version'])}
        else:
            return None

    def services(self):
        """
        Return the services implemented by this Slice Authority.
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
        return self._resource_manager_tools.form_api_versions(hostname, port, endpoints)

    def credential_types(self):
        """
        Return the credential types implemented by this Slice Authority.
        """
        return self.SUPPORTED_CREDENTIAL_TYPES


    #--- object methods
    def create_slice(self, client_cert, credentials, fields, options):
        """
        Create a slice object.

        Generate fields for a new object:
            * SLICE_URN: retrieve the hostname from the Flask AMsoil plugin
                and form into a valid URN
            * SLICE_UID: generate a new UUID4 value
            * SLICE_CREATION: get the time now and convert it into RFC3339 form
            * SLICE_EXPIRED: slice object has just been created, so it is has not
                yet expired

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        fields['SLICE_URN'] = 'urn:publicid+IDN+' + hostname + '+slice+' + fields.get('SLICE_NAME')
        fields['SLICE_UID'] = str(uuid.uuid4())
        fields['SLICE_CREATION'] = pyrfc3339.generate(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        fields['SLICE_EXPIRED'] = False
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'slice')

    def update_slice(self, urn, client_cert, credentials, fields, options):
        """
        Update a slice object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'slice', {'SLICE_URN':urn})

    def lookup_slice(self, client_cert, credentials, match, filter_, options):
        """
        Lookup a slice object.
        """

        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'slice', match, filter_)

    def create_sliver_info(self, client_cert, credentials, fields, options):
        """
        Create a sliver information object.
        """
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'sliver_info')

    def update_sliver_info(self, urn, client_cert, credentials, fields, options):
        """
        Update a sliver information object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'sliver_info', {'SLIVER_INFO_URN':urn})

    def lookup_sliver_info(self, client_cert, credentials, match, filter_, options):
        """
        Lookup a sliver information object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'sliver_info', match, filter_)

    def delete_sliver_info(self, urn, client_cert, credentials, options):
        """
        Delete a sliver information object.
        """
        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME, 'sliver_info', {'SLIVER_INFO_URN':urn})

    def create_project(self, client_cert, credentials, fields, options):
        """
        Create a project object.

        Generate fields for a new object:
            * PROJECT_URN: retrieve the hostname from the Flask AMsoil plugin
                and form into a valid URN
            * PROJECT_UID: generate a new UUID4 value
            * PROJECT_CREATION: get the time now and convert it into RFC3339 form
            * PROJECT_EXPIRED: project object has just been created, so it is
                has not yet expired

        """
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        fields['PROJECT_URN'] = 'urn:publicid+IDN+' + hostname + '+project+' + fields.get('PROJECT_NAME')
        fields['PROJECT_UID'] = str(uuid.uuid4())
        fields['PROJECT_CREATION'] = pyrfc3339.generate(datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        fields['PROJECT_EXPIRED'] = False
        return self._resource_manager_tools.object_create(self.AUTHORITY_NAME, fields, 'project')

    def update_project(self, urn, client_cert, credentials, fields, options):
        """
        Update a project object.
        """
        return self._resource_manager_tools.object_update(self.AUTHORITY_NAME, fields, 'project', {'PROJECT_URN':urn})

    def delete_project(self, urn, client_cert, credentials, options):
        """
        Delete a project object.
        """
        return self._resource_manager_tools.object_delete(self.AUTHORITY_NAME, 'project', {'PROJECT_URN':urn})

    def lookup_project(self, client_cert, credentials, match, filter_, options):
        """
        Lookup a project object.
        """
        return self._resource_manager_tools.object_lookup(self.AUTHORITY_NAME, 'project', match, filter_)

    def modify_slice_membership(self, urn, certificate, credentials, options):
        """
        Modify a slice membership object.
        """
        return self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'slice_member', urn, options, 'SLICE_MEMBER', 'SLICE_URN')

    def modify_project_membership(self, urn, certificate, credentials, options):
        """
        Modify a project membership object.
        """
        return self._resource_manager_tools.member_modify(self.AUTHORITY_NAME, 'project_member', urn, options, 'PROJECT_MEMBER', 'PROJECT_URN')

    def lookup_slice_membership(self, urn, certificate, credentials, options):
        """
        Lookup a slice membership object.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'slice_member', 'SLICE_URN', urn, ['SLICE_URN'])

    def lookup_project_membership(self, urn, certificate, credentials, options):
        """
        Lookup a project membership object.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'project_member', 'PROJECT_URN', urn, ['PROJECT_URN'])

    def lookup_slice_membership_for_member(self, member_urn, certificate, credentials, options):
        """
        Lookup a slice membership object for a given member.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'slice_member', 'SLICE_MEMBER', member_urn, ['SLICE_MEMBER'])

    def lookup_project_membership_for_member(self, member_urn, certificate, credentials, options):
        """
        Lookup a project membership object for a given member.
        """
        return self._resource_manager_tools.member_lookup(self.AUTHORITY_NAME, 'project_member', 'PROJECT_MEMBER', member_urn, ['PROJECT_MEMBER'])

