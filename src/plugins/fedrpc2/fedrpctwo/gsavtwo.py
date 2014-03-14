import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gsarpc')

import gapitools

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GSAv2Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GSAv2Handler, self).__init__(logger)
        self._delegate = None
    
    # ---- General methods
    @serviceinterface
    def setDelegate(self, adelegate):
        self._delegate = adelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

    def get_version(self):
        """Delegates the call and unwraps the needed parameter."""
        try:
            version, add_services, credential_types, fields = self._delegate.get_version(self.requestCertificate())
            result = {}
            result['VERSION'] = version
            result['CREDENTIAL_TYPES'] = credential_types
            result['SERVICES'] = ['MEMBER'] + add_services
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    # ---- Member Service Methods
    def lookup_public_member_info(self, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.lookup_public_member_info(self.requestCertificate(), field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def lookup_identifying_member_info(self, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.lookup_identifying_member_info(self.requestCertificate(), credentials, field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def lookup_private_member_info(self, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.lookup_private_member_info(self.requestCertificate(), credentials, field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def update_member_info(self, member_urn, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet")
    def get_credentials(self, member_urn, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 

    # ---- Key Service Methods
    def create_key(self, member_urn, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 

    def delete_key(self, member_urn, key_id, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 

    def update_key(self, member_urn, key_id, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 

    def lookup_keys(self, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        raise GFedv2NotImplementedError("Method not implemented yet") 
    



class GSAv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    {match}, {filter} and {fields} semantics are explained in the GENI Federation API document.
    """
    
    def __init__(self):
        super(GSAv2DelegateBase, self).__init__()
    
    # ---- General methods
    
    def get_version(self, client_cert):
        """
        Return information about version and options (filter, query, credential types) accepted by this member authority
        NB: This is an unprotected call, no client cert required.
        
        This method shall return (in this order)
        - a version string (e.g. "1.0.3")
        - a list of additional services (additional to 'MEMBER') provided by the MA e.g. [] or ['KEY']
        - accepted credential types (e.g. "CREDENTIAL_TYPES": {"SFA": "1"}, "ABAC" : ["1", "2"]})
        - None or a dictionary of custom fields (e.g. {"TYPE" : "URN"}, for more info and available types, please see the API spec (http://groups.geni.net/geni/wiki/UniformClearinghouseAPI#APIget_versionmethods))
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    # ---- Member Service Methods
    MEMBER_DEFAULT_FIELDS = {
        "MEMBER_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of given member",
            "MATCH"	  : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_UID" : {
            "TYPE"    : "UID",
            "DESC"    : "UID (unique within authority) of member",
            "MATCH"	  : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_FIRSTNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "First name of member",
            "MATCH"	  : True,
            "PROTECT" : "IDENTIFYING"},
        "MEMBER_LASTNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Last name of member",
            "MATCH"	  : True,
            "PROTECT" : "IDENTIFYING"},
        "MEMBER_USERNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Username of user",
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_EMAIL" : {
            "TYPE"    : "STRING",
            "DESC"    : "Email of user",
            "MATCH"   : False,
            "PROTECT" : "IDENTIFYING"}}
    
    def lookup_public_member_info(self, client_cert, field_filter, field_match, options):
        """
        Lookup public information about members matching given criteria.
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup_identifying_member_info(self, client_cert, credentials, field_filter, field_match, options):
        """
        Lookup identifying (e.g. name, email) info about matching members Arguments:
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup_private_member_info(self, client_cert, credentials, field_filter, field_match, options):
        """
        Lookup private (SSL/SSH key) information about members matching given criteria Arguments:
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def update_member_info(self, client_cert, member_urn, credentials, update_dict, options):
        """
        Update information about given member public, private or identifying information
        Arguments:
          member_urn: URN of member for whom to set information
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def get_credentials(self, client_cert, member_urn, credentials, options):
        """
        Provide list of credentials (signed statements) for given member
        This is member-specific information suitable for passing as credentials in an AM API call for aggregate authorization.
        Arguments:
          member_urn: URN of member for which to retrieve credentials
          options: Potentially contains 'speaking-for' key indicating a speaks-for invocation (with certificate of the accountable member in the credentials argument)
        Return: List of credentials in "CREDENTIAL_LIST" format, i.e. a list of credentials with type information suitable for passing to aggregates speaking AM API V3.
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
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
    
    def create_key(self, client_cert, member_urn, credentials, create_dict, options):
        """
        Create a record for a key pair for given member
        Arguments:
          member_urn: URN of member for which to retrieve credentials
          options: 'fields' containing the fields for the key pair being stored
        Return:
          Dictionary of name/value pairs for created key record including the KEY_ID

          Should return DUPLICATE_ERROR if a key with the same KEY_ID is already stored for given user
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def delete_key(self, client_cert, member_urn, key_id, credentials, options):
        """
        Delete a key pair for given member
        Arguments:
          member_urn: urn of member for which to delete key pair
          key_id: KEY_ID (fingerprint) of key pair to be deleted
        Return:
          True if succeeded
        Should return ARGUMENT_ERROR if no such key is found for user
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def update_key(self, client_cert, member_urn, key_id, credentials, update_dict, options):
        """
        Update the details of a key pair for given member
        Arguments:
          member_urn: urn of member for which to delete key pair
          key_id: KEY_ID (fingerprint) of key pair to be deleted
          options: 'fields' containing fields for key pairs that are permitted for update
        Return:
          True if succeeded
        Should return ARGUMENT_ERROR if no such key is found for user
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup_keys(self, client_cert, credentials, field_filter, field_match, options):
        """
        Lookup keys for given match criteria return fields in given filter criteria
        Arguments:
          options: 'match' for query match criteria, 'filter' for fields to be returned
        Return:
          Dictionary (indexed by member_urn) of dictionaries containing name/value pairs for all keys registered for that given user.
        More info see: http://groups.geni.net/geni/wiki/UniformClearinghouseAPI
        """
        raise GFedv2NotImplementedError("Method not implemented")
    
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
