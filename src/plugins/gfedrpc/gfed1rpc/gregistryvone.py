import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gch1rpc')

import gapitools
# from amsoil.config import ROOT_PATH
# from amsoil.config import expand_amsoil_path

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GRegv1Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GRegv1Handler, self).__init__(logger)
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
            version, fields = self._delegate.get_version(self.requestCertificate())
            result = {}
            result['VERSION'] = version
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def get_aggregates(self, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.get_aggregates(self.requestCertificate(), field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def get_member_authorities(self, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.get_member_authorities(self.requestCertificate(), field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def get_slice_authorities(self, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.get_slice_authorities(self.requestCertificate(), field_filter, field_match, options)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def lookup_authorities_for_urns(self, urns):
        """Delegates the call and unwraps the needed parameter."""
        try:
            result = self._delegate.lookup_authorities_for_urns(self.requestCertificate(), urns)
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)
        
    def get_trust_roots(self):
        """Delegates the call and unwraps the needed parameter."""
        try:
            result = self._delegate.get_trust_roots(self.requestCertificate())
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

class GRegv1DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Clearinghouse API (v1). 
    {match}, {filter} and {fields} semantics are explained in the GENI CH API document.
    {client_cert} might be None if the user connects without SSL.
    """

    DEFAULT_FIELDS = {
        "SERVICE_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of given service"},
        "SERVICE_URL" : {
            "TYPE"    : "URL",
            "DESC"    : "URL by which to contact the service"},
        "SERVICE_CERT" : {
            "TYPE"    : "CERTIFICATE",
            "DESC"    : "Public certificate of service"},
        "SERVICE_NAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Short name of service"},
        "SERVICE_DESCRIPTION" : {
            "TYPE"    : "STRING",
            "DESC"    : "Descriptive name of service"}
        }

    def __init__(self):
        super(GRegv1DelegateBase, self).__init__()
    
    def get_version(self, client_cert):
        """Overwrite this method in the actual delegate implementation.
        Provide a structure detailing the version information as well as details of accepted options s for CH API calls.
        NB: This is an unprotected call, no client cert required.
        
        This method shall return
        - a version string (e.g. 1.0.3)
        - None or a dictionary of custom CH fields (e.g. {"TYPE" : "URN"}, for more info and available types, please see the API spec (http://groups.geni.net/geni/wiki/UniformClearinghouseAPI#APIget_versionmethods))
        """
        raise GFedv1NotImplementedError("Method not implemented")
        
    def get_aggregates(self, client_cert, field_filter, field_match, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all aggregates associated with the Federation.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv1NotImplementedError("Method not implemented")

    def get_member_authorities(self, client_cert, field_filter, field_match, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all MA's associated with the Federation.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv1NotImplementedError("Method not implemented")
        
    def get_slice_authorities(self, client_cert, field_filter, field_match, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all SA's associated with the Federation
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv1NotImplementedError("Method not implemented")
        
    def lookup_authorities_for_urns(self, client_cert, urns):
        """Overwrite this method in the actual delegate implementation.
        Lookup the authorities for a given URNs. There should be at most one (potentially none) per URN.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv1NotImplementedError("Method not implemented")
        
    def get_trust_roots(self, client_cert):
        """Overwrite this method in the actual delegate implementation.
        Return list of trust roots (certificates) associated with this CH.
        Often this is a concatenatation of the trust roots of the included authorities.
        Should return a list of strings.
        NB: This is an unprotected call, no client cert required."""
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