import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gmarpc')

xmlrpc = pm.getService('xmlrpc')

class GMAv2Handler(xmlrpc.Dispatcher):
    """
    Handle XML-RPC Member Authority API calls.
    """

    def __init__(self):
        """
        Initialise logger and clear delegate.
        """
        super(GMAv2Handler, self).__init__(logger)
        self._api_tools = pm.getService('apitools')
        self._delegate = None

    # ---- General methods
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
        Get details for this Member Authority implementation.

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

class GMAv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    """

    def __init__(self):
        super(GMAv2DelegateBase, self).__init__()

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

    def get_credentials(self, member_urn, credentials, options):
        """
        Provide list of credentials (signed statements) for given member
        This is member-specific information suitable for passing as credentials in
         an AM API call for aggregate authorization.
        Arguments:
           member_urn: URN of member for which to retrieve credentials
           options: Potentially contains 'speaking_for' key indicating a speaks-for
               invocation (with certificate of the accountable member in the credentials argument)

        Return:
            List of credential in 'CREDENTIALS' format, i.e. a list of credentials with
               type information suitable for passing to aggregates speaking AM API V3.
        """
        raise GFedv2NotImplementedError("Method not implemented")
