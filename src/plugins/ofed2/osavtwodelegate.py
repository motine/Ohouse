import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GSAv2DelegateBase = pm.getService('gsav2delegatebase')
gfed_ex = pm.getService('apiexceptions')
VERSION = '2'

class OSAv2Delegate(GSAv2DelegateBase):
    """
    Implements Slice Authority methods.

    Does validity checking on passed options.
    """

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Retrieve whitelists for use in validity checking.
        """
        self._slice_authority_resource_manager = pm.getService('osliceauthorityrm')
        self._delegate_tools = pm.getService('delegatetools')
        self._api_tools = pm.getService('apitools')
        self._slice_whitelist = self._delegate_tools.get_whitelist('SLICE')
        self._sliver_info_whitelist = self._delegate_tools.get_whitelist('SLIVER_INFO')
        self._project_whitelist = self._delegate_tools.get_whitelist('PROJECT')

    def get_version(self):
        """
        Get implementation details from resource manager. Supplement these with
        additional details specific to the delegate.
        """
        version = self._delegate_tools.get_version(self._slice_authority_resource_manager)
        version['VERSION'] = VERSION
        version['FIELDS'] = self._delegate_tools.get_supplementary_fields(['SLICE', 'SLIVER', 'PROJECT'])
        return version

    def create(self, type_, certificate, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'create' call; if valid, create this object using
        the resource manager.
        """
        if (type_=='SLICE'):
            self._delegate_tools.object_creation_check(fields, self._slice_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            self._delegate_tools.slice_name_check(fields.get('SLICE_NAME')) #Specific check for slice name restrictionas
            return self._slice_authority_resource_manager.create_slice(certificate, credentials, fields, options)
        elif (type_=='SLIVER_INFO'):
            self._delegate_tools.object_creation_check(fields, self._sliver_info_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.create_sliver_info(certificate, credentials, fields, options)
        elif (type_=='PROJECT'):
            self._delegate_tools.object_creation_check(fields, self._project_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.create_project(certificate, credentials, fields, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No create method found for object type: " + str(type_))

    def update(self, type_, urn, certificate, credentials, fields, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'update' call; if valid, update this object using
        the resource manager.
        """
        if (type_ == 'SLICE') :
            update_expiration_time = fields.get('SLICE_EXPIRATION')

            if update_expiration_time:
                lookup_result = self._slice_authority_resource_manager.lookup_slice(certificate, credentials,
                                                                                     {'SLICE_URN' : str(urn)}, [], {})

                # keyed_lookup_result enables referencing an dicitionary with any chosen key_name. For example,
                # SLICE_URN can be used as the key for the dictionary return when looking up a slice.
                # This is needed here to enable fetching out the SLICE_CREATION time belonging to a certain SLICE_URN
                keyed_lookup_result = self._delegate_tools.to_keyed_dict(lookup_result, "SLICE_URN")
                is_valid = self._delegate_tools.validate_expiration_time(str(keyed_lookup_result[urn]['SLICE_CREATION']),
                                                                        update_expiration_time)

                if not is_valid:
                    raise gfed_ex.GFedv2ArgumentError("Invalid expiry date for object type: " + str(type_))

            self._delegate_tools.object_update_check(fields, self._slice_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.update_slice(urn, certificate, credentials, fields, options)
        elif (type_=='SLIVER_INFO'):
            self._delegate_tools.object_update_check(fields, self._sliver_info_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.update_sliver_info(urn, certificate, credentials, fields, options)
        elif (type_=='PROJECT'):
            self._delegate_tools.object_update_check(fields, self._project_whitelist)
            self._delegate_tools.object_consistency_check(type_, fields)
            return self._slice_authority_resource_manager.update_project(urn, certificate, credentials, fields, options)

        else:
            raise gfed_ex.GFedv2NotImplementedError("No update method found for object type: " + str(type_))

    def delete(self, type_, urn, certificate, credentials, options):
        """
        Depending on the object type defined in the request, delete this object
        using the resource manager.
        """
        if (type_=='SLICE'):
            raise gfed_ex.GFedv2NotImplementedError("No authoritative way to know that there aren't live slivers associated with a slice.")
        elif (type_=='SLIVER_INFO'):
            return self._slice_authority_resource_manager.delete_sliver_info(urn, certificate, credentials, options)
        elif (type_=='PROJECT'):
            return self._slice_authority_resource_manager.delete_project(urn, certificate, credentials,  options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No delete method found for object type: " + str(type_))

    def lookup(self, type_, certificate, credentials, match, filter_, options):
        """
        Depending on the object type defined in the request, lookup this object
        using the resource manager.
        """
        if (type_=='SLICE'):

            result = self._slice_authority_resource_manager.lookup_slice(certificate, credentials, match, filter_, options)
            return self._delegate_tools.to_keyed_dict(result, "SLICE_URN")
        elif (type_=='SLIVER_INFO'):
            return self._delegate_tools.to_keyed_dict(self._slice_authority_resource_manager.lookup_sliver_info(certificate, credentials, match, filter_, options), "SLIVER_INFO_URN")
        elif (type_=='PROJECT'):
            return self._delegate_tools.to_keyed_dict(self._slice_authority_resource_manager.lookup_project(certificate, credentials, match, filter_, options), "PROJECT_URN")
        else:
            raise gfed_ex.GFedv2NotImplementedError("No lookup method found for object type: " + str(type_))

        # ---- Slice Member Service Methods and Project Member Service Methods
    def modify_membership(self, type_, urn, certificate, credentials, options):
        """
        Depending on the object type defined in the request, check the validity
        of passed fields for a 'modify_membership' call; if valid, modify the
        membership for the given URN using the resource manager.
        """
        if (type_=='SLICE'):

            self._delegate_tools.member_check(['SLICE_MEMBER', 'SLICE_ROLE'],options)
            return self._slice_authority_resource_manager.modify_slice_membership(urn, certificate, credentials, options)
        elif (type_=='PROJECT'):
            self._delegate_tools.member_check(['PROJECT_MEMBER', 'PROJECT_ROLE'], options)
            return self._slice_authority_resource_manager.modify_project_membership(urn, certificate, credentials, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No membership modification method found for object type: " + str(type_))

    def lookup_members(self, type_, urn, certificate, credentials, options):
        """
        Depending on the object type defined in the request, lookup members for
        a given URN using the resource manager.
        """
        if (type_=='SLICE'):
            return self._slice_authority_resource_manager.lookup_slice_membership(urn, certificate, credentials, options)
        elif (type_=='PROJECT'):
            return self._slice_authority_resource_manager.lookup_project_membership(urn, certificate, credentials, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No member lookup method found for object type: " + str(type_))

    def lookup_for_member(self, type_, member_urn, certificate, credentials, options):
        """
        Depending on the object type defined in the request, lookup details for
        a member using the resource manager.
        """
        if (type_=='SLICE'):
            return self._slice_authority_resource_manager.lookup_slice_membership_for_member(member_urn, certificate, credentials, options)
        elif (type_=='PROJECT'):
            return self._slice_authority_resource_manager.lookup_project_membership_for_member(member_urn, certificate, credentials, options)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No lookup for member method found for object type: " + str(type_))

