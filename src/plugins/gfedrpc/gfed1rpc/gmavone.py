import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gch1rpc')

import gapitools

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GMAv1Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GMAv1Handler, self).__init__(logger)
        self._delegate = None
    
    @serviceinterface
    def setDelegate(self, adelegate):
        self._delegate = adelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

    def get_version(self):
        """Delegates the call and unwraps the needed parameter."""
        try:
            version, credential_types, fields = self._delegate.get_version(self.requestCertificate())
            result = {}
            result['VERSION'] = version
            result['CREDENTIAL_TYPES'] = credential_types
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

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
        pass
    def get_credentials(self, member_urn, credentials, options):
        """Delegates the call and unwraps the needed parameter."""
        pass


class GMAv1DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v1).
    {match}, {filter} and {fields} semantics are explained in the GENI Federation API document.
    """
    
    DEFAULT_FIELDS = {
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

    def __init__(self):
        super(GMAv1DelegateBase, self).__init__()
    
    def get_version(self, client_cert):
        """
        Return information about version and options (filter, query, credential types) accepted by this member authority
        NB: This is an unprotected call, no client cert required.
        
        This method shall return (in this order)
        - a version string (e.g. "1.0.3")
        - accepted credential types (e.g. "CREDENTIAL_TYPES": {"SFA": "1"}, "ABAC" : ["1", "2"]})
        - None or a dictionary of custom fields (e.g. {"TYPE" : "URN"}, for more info and available types, please see the API spec (http://groups.geni.net/geni/wiki/UniformClearinghouseAPI#APIget_versionmethods))
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_public_member_info(self, client_cert, field_filter, field_match, options):
        """
        Lookup public information about members matching given criteria.
        NB: This is an unprotected call, no client cert required.
        Returns a list of dictionaries
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_identifying_member_info(self, client_cert, credentials, field_filter, field_match, options):
        """
        Lookup identifying (e.g. name, email) info about matching members Arguments:
        Returns a list of dictionaries
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_private_member_info(self, client_cert, credentials, field_filter, field_match, options):
        """
        Lookup private (SSL/SSH key) information about members matching given criteria Arguments:
        Returns a list of dictionaries
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def update_member_info(self, client_cert, member_urn, credentials, update_dict, options):
        """
        Update information about given member public, private or identifying information
        Arguments:
          member_urn: URN of member for whom to set information
        Returns nothing
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def get_credentials(self, client_cert, member_urn, credentials, options):
        """
        Provide list of credentials (signed statements) for given member
        This is member-specific information suitable for passing as credentials in an AM API call for aggregate authorization.
        Arguments:
          member_urn: URN of member for which to retrieve credentials
          options: Potentially contains 'speaking-for' key indicating a speaks-for invocation (with certificate of the accountable member in the credentials argument)
        Return: List of credentials in "CREDENTIAL_LIST" format, i.e. a list of credentials with type information suitable for passing to aggregates speaking AM API V3.
        """
        raise GFedv1NotImplementedError("Method not implemented")
    
    # -- helper methods
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
