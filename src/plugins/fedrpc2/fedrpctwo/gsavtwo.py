import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gsarpc')

xmlrpc = pm.getService('xmlrpc')

class GSAv2Handler(xmlrpc.Dispatcher):
    """
    Handle XML-RPC Slice Authority API calls.
    """

    def __init__(self):
        """
        Initialise logger and clear delegate.
        """
        super(GSAv2Handler, self).__init__(logger)
        self._api_tools = pm.getService('apitools')
        self._delegate = None

    # ---- General Methods
    @serviceinterface
    def setDelegate(self, adelegate):
        """
        Set this object's delegate.
        """
        self._delegate = adelegate

    @serviceinterface
    def getDelegate(self):
        """
        Get this object's delegate.
        """
        return self._delegate

    def get_version(self):
        """
        Get details for this Slice Authority implementation.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.get_version()
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def create(self, type_, credentials, options):
        """
        Create object of given type with fields given in options.

        Unwrap 'fields' out of 'options'.

        Call delegate method and return result or exception.

        """
        try:
            fields = self._api_tools.fetch_fields(options)
            result = self._delegate.create(type_, self.requestCertificate(), credentials, fields, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def update(self, type_, urn, credentials, options):
        """
        Update object of given type and URN with fields given in options.

        Unwrap 'fields' out of 'options'.

        Call delegate method and return result or exception.

        """
        try:
            fields = self._api_tools.fetch_fields(options)
            result = self._delegate.update(type_, urn, self.requestCertificate(), credentials, fields, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def delete(self, type_, urn, credentials, options):
        """
        Delete object of given type and URN.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.delete(type_, urn, self.requestCertificate(), credentials, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def lookup(self, type_, credentials, options):
        """
        Lookup objects with given type.

        Unwrap 'match' and 'filter' fields out of 'options'.

        Call delegate method and return result or exception.

        """
        try:
            match, filter_ = self._api_tools.fetch_match_and_filter(options)
            result = self._delegate.lookup(type_, self.requestCertificate(), credentials, match, filter_, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    # ---- Slice Member Service Methods and Project Member Service Methods
    def modify_membership(self, type_, urn, credentials, options):
        """
        Modify information for members that belong to a particular PROJECT or SLICE with given URN.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.modify_membership(type_, urn, self.requestCertificate(), credentials, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def lookup_members(self, type_, urn, credentials, options):
        """
        Lookup information for members that belong to a particular PROJECT or SLICE with given URN.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.lookup_members(type_, urn, self.requestCertificate(), credentials, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def lookup_for_member(self, type_, member_urn, credentials, options):
        """
        Lookup information for a individual member with given URN.

        Call delegate method and return result or exception.
        """
        try:
            result = self._delegate.lookup_for_member(type_, member_urn, self.requestCertificate(), credentials, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

class GSAv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    """

    def __init__(self):
        super(GSAv2DelegateBase, self).__init__()

    # ---- General methods
    def get_version(self):
        """
        Return information about version and options
          (e.g. filter, query, credential types) accepted by this service

        Arguments: None

        Return:
            get_version structure information as described above
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def create(self, type_, credentials, options):
        """
        Creates a new instance of the given object with a 'fields' option
        specifying particular field values that are to be associated with the object.
        These may only include those fields specified as 'ALLOWED or 'REQUIRED'
        in the 'Creation' column of the object descriptions below
        or in the 'CREATE' key in the supplemental fields in the
        get_version specification for that object.
        If successful, the call returns a dictionary of the fields
        associated with the newly created object.


        Arguments:

           type : type of object to be created
          options:
              'fields', a dictionary field/value pairs for object to be created

        Return:
          Dictionary of object-type specific field/value pairs for created object
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def update(self, type_, urn, credentials, options):
        """
        Updates an object instance specified by URN with a 'fields' option
         specifying the particular fields to update.
        Only a single object can be updated from a single update call.
        The fields may include those specified as 'Yes' in the 'Update' column
        of the object descriptions below, or 'TRUE' in the 'UPDATE' key in the
        supplemental fields provided by the get_version call.
        Note: There may be more than one entity of a given URN at an authority,
        but only one 'live' one (any other is archived and cannot be updated).

        Arguments:
          type: type of object to be updated
          urn: URN of object to update
            (Note: this may be a non-URN-formatted unique identifier e.g. in the case of keys)
          options: Contains 'fields' key referring dictionary of
               name/value pairs to update

        Return: None
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def delete(self, type_, urn, credentials, options):
        """
        Deletes an object instance specified by URN
        Only a single object can be deleted from a single delete call.
        Note: not all objects can be deleted. In general, it is a matter
            of authority policy.

        Arguments:
          type: type of object to be deleted
          urn: URN of object to delete
            (Note: this may be a non-URN-formatted unique identifier e.g. in the case of keys)

        Return: None
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup(self, type_, credentials, options):
        """
        Lookup requested details for objects matching 'match' options.
        This call takes a set of 'match' criteria provided in the 'options' field,
        and returns a dictionary of dictionaries of object attributes
        keyed by object URN matching these criteria.
        If a 'filter' option is provided, only those attributes listed in the 'filter'
        options are returned.
        The requirements on match criteria supported by a given service
        are service-specific; however it is recommended that policies
        restrict lookup calls to requests that are bounded
        to particular sets of explicitly listed objects (and not open-ended queries).

        See additional details on the lookup method in the document section below.


        Arguments:
           type: type of objects for which details are being requested
           options: What details to provide (filter options)
                   for which objects (match options)

        Return: List of dictionaries (indexed by object URN) with field/value pairs
          for each returned object
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def get_credentials(self, slice_urn, credentials, options):
        """
        Provide list of credentials for the caller relative to the given slice.
        If the invocation is in a speaks-for context, the credentials will be for the
        'spoken-for' member, not the invoking tool.

        For example, this call may return a standard SFA Slice Credential and some
        ABAC credentials indicating the role of the member with respect to the slice.

        Note: When creating an SFA-style Slice Credential, the following roles
        typically allow users to operate at known GENI-compatible
        aggregates: "*" (asterisk)  or the list of "refresh", "embed",
           "bind", "control" "info".

        Arguments:
          slice_urn: URN of slice for which to get member's credentials
          options: Potentially contains 'speaking_for' key indicating a speaks-for
             invocation (with certificate of the accountable member
             in the credentials argument)

        Return:
          List of credential in 'CREDENTIALS' format, i.e. a list of credentials with
        type information suitable for passing to aggregates speaking AM API V3.
        """
        raise GFedv2NotImplementedError("Method not implemented")

    # ---- Slice Member Service Methods and Project Member Service Methods
    def modify_membership(self, type_, urn, credentials, options):
        """
        Modify object membership, adding, removing and changing roles of members
           with respect to given object

        Arguments:
          type: type of object for whom to lookup membership (
              in the case of Slice Member Service, "SLICE",
              in the case of Project Member Service, "PROJECT")
          urn: URN of slice/project for which to modify membership
          Options:
              members_to_add: List of member_urn/role tuples for members to add to
                     slice/project of form
                        {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}
                           (or 'PROJECT_MEMBER/PROJECT_ROLE
                           for Project Member Service)
              members_to_remove: List of member_urn of members to
                       remove from slice/project
              members_to_change: List of member_urn/role tuples for
                        members whose role
                       should change as specified for given slice/project of form
                       {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}
                       (or 'PROJECT_MEMBER/PROJECT_ROLE for Project Member Service)

        Return:
          None
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup_members(self, type_, urn, credentials, options):
        """
        Lookup members of given object and their roles within that object

        Arguments:
          type: type of object for whom to lookup membership
                 (in the case of Slice Member Service, "SLICE",
                  in the case of Project Member Service, "PROJECT")
          urn: URN of object for which to provide current members and roles

        Return:
           List of dictionaries of member_urn/role pairs
              [{'SLICE_MEMBER': member_urn,
               'SLICE_ROLE': role }...]
                (or PROJECT_MEMBER/PROJECT_ROLE
                 for Project Member Service)
                 where 'role' is a string of the role name.
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup_for_member(self, type_, member_urn, credentials, options):
        """
        Lookup objects of given type for which the given member belongs

        Arguments:
          Member_urn: The member for whom to find slices to which it belongs

        Return:
           List of dictionary of urn/role pairs
               [('SLICE_URN' : slice_urn, 'SLICE_ROLE' : role} ...]
               (or PROJECT_MEMBER/PROJECT_ROLE
                  for Project Member Service)
               for each object to which a member belongs,
               where role is a string of the role name
        """
        raise GFedv2NotImplementedError("Method not implemented")
