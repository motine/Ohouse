import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gmarpc')

import gapitools

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GMAv2Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GMAv2Handler, self).__init__(logger)
        self._delegate = None
    
    # ---- General methods
    @serviceinterface
    def setDelegate(self, adelegate):
        self._delegate = adelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

    def get_version(self):
        try:
            version, urn, implementation, services, credential_types, api_versions, fields = self._delegate.get_version()
            result = {}
            result['VERSION'] = version
            result['URN'] = urn
            if implementation:
                result['IMPLEMENTATION'] = implementation
            if services:
                result['SERVICES'] = services
            result['CREDENTIAL_TYPES'] = credential_types
            result['API_VERSIONS'] = api_versions
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def create(self, _type, credentials, options):
        try:
            result = self._delegate.create(_type, self.requestCertificate(), options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def update(self, _type, urn, credentials, options):
        try:
            result = self._delegate.update(_type, self.requestCertificate(), options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def delete(self, _type, urn, credentials, options):
        try:
            result = self._delegate.delete(_type, self.requestCertificate(), options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def lookup(self, _type, credentials, options):
        try:
            field_match, field_filter = gapitools.fetch_match_and_filter(options)
            print field_match
            result = self._delegate.lookup(_type, self.requestCertificate(), credentials, field_match, field_filter, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    # ---- Member Service Methods
    def get_credentials(self, member_urn, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 

    

class GMAv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    {match}, {filter} and {fields} semantics are explained in the GENI Federation API document.
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

    def create(self, _type, credentials, options):
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

    def update(self, _type, urn, credentials, options):
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

    def delete(self, _type, urn, credentials, options):
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

    def lookup(self, _type, credentials, options):
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

    def get_credentials(self, client_cert, member_urn, credentials, options):
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
    
    # ---- Key Service Methods
    KEY_DEFAULT_FIELDS = {
        "KEY_MEMBER" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of member associated with key pair",
            "MATCH"	  : True,
            "CREATE"  : "REQUIRED",
            "UPDATE"  : False },
        "KEY_ID" : {
            "TYPE"    : "STRING",
            "DESC"    : "Unique identifier of key: typically a fingerprint or hash of public key",
            "MATCH"	  : True,
            "CREATE"  : "REQUIRED",
            "UPDATE"  : False },
        "KEY_TYPE" : {
            "TYPE"    : "STRING",
            "DESC"    : "Type of key (e.g. PEM, openssh, rsa-ssh)",
            "MATCH"   : True,
            "CREATE"  : "REQUIRED",
            "UPDATE"  : False },
        "KEY_PUBLIC" : {
            "TYPE"    : "KEY",
            "DESC"    : "Public key value",
            "MATCH"	  : True,
            "CREATE"  : "REQUIRED",
            "UPDATE"  : False },
        "KEY_PRIVATE" : {
            "TYPE"    : "KEY",
            "DESC"    : "Private key value",
            "MATCH"	  : True,
            "CREATE"  : "ALLOWED",
            "UPDATE"  : False },
        "KEY_DESCRIPTION" : {
            "TYPE"    : "STRING",
            "DESC"    : "Human readable description of key pair",
            "MATCH"	  : True,
            "CREATE"  : "ALLOWED",
            "UPDATE"  : True }}
    
    # ---- helper methods
    def _match_and_filter_and_to_dict(self, list_of_dicts, key_field, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter_and_to_dict(list_of_dicts, key_field, field_filter, field_match)
    
    def _match_and_filter(self, list_of_dicts, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter(list_of_dicts, field_filter, field_match)
    
    def _filter_fields(self, d, field_filter):
        """see documentation in gapitools"""
        return gapitools.filter_fields(d, field_filter)

    def _does_match_fields(self, d, field_match):
        """see documentation in gapitools"""
        return gapitools.does_match_fields(d, field_match)
