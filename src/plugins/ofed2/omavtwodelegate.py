import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GMAv2DelegateBase = pm.getService('gmav2delegatebase')
gfed_ex = pm.getService('apiexceptions')

VERSION = '2'

class OMAv2Delegate(GMAv2DelegateBase):
    """
    Implements Member Authority methods.

    Does validity checking on passed options.
    """

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Retrieve whitelists for use in validity checking.
        """
        self._member_authority_resource_manager = pm.getService('omemberauthorityrm')
        self._delegate_tools = pm.getService('delegatetools')
        self._member_whitelist = self._delegate_tools.get_whitelist('MEMBER')
        self._key_whitelist = self._delegate_tools.get_whitelist('KEY')

    def get_version(self):
        """
        Get implementation details from resource manager. Supplement these with
        additional details specific to the delegate.
        """
        version = self._delegate_tools.get_version(self._member_authority_resource_manager)
        version['VERSION'] = VERSION
        version['FIELDS'] = self._delegate_tools.get_supplementary_fields(['MEMBER', 'KEY'])
        return version

    def create(self, type_, certificate, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'create' call; if valid, create this object using
        the resource manager.
        """
        if (type_=='KEY'):
            self._delegate_tools.object_creation_check(fields, self._key_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._member_authority_resource_manager.create_key(certificate, credentials, fields, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No create method found for object type: " + str(type_))

    def update(self, type_, urn, certificate, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'update' call; if valid, update this object using
        the resource manager.
        """
        if (type_=='MEMBER'):
            self._delegate_tools.object_update_check(fields, self._member_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._member_authority_resource_manager.update_member(urn, certificate, credentials, fields, options)
        elif (type_=='KEY'):
            self._delegate_tools.object_update_check(fields, self._key_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._member_authority_resource_manager.update_key(urn, certificate, credentials, fields, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No update method found for object type: " + str(type_))

    def delete(self, type_, urn, certificate, credentials, options):
        """
        Depending on the object type defined in the request, delete this object
        using the resource manager.
        """
        if (type_=='KEY'):
            return self._member_authority_resource_manager.delete_key(urn, certificate, credentials, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No delete method found for object type: " + str(type_))

    def lookup(self, type_, certificate, credentials, match, filter_, options):
        """
        Depending on the object type defined in the request, lookup this object
        using the resource manager.
        """
        if (type_=='MEMBER'):
            return self._delegate_tools.to_keyed_dict(self._member_authority_resource_manager.lookup_member(certificate, credentials, match, filter_, options), "MEMBER_URN")
        elif (type_=='KEY'):
            return self._delegate_tools.to_keyed_dict(self._member_authority_resource_manager.lookup_key(certificate, credentials, match, filter_, options), "KEY_ID")
        else:
            raise gfed_ex.GFedv2NotImplementedError("No lookup method found for object type: " + str(type_))
