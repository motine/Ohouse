import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gregistryrpc')

import gapitools
# from amsoil.config import ROOT_PATH
# from amsoil.config import expand_amsoil_path

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GRegistryv2Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GRegistryv2Handler, self).__init__(logger)
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
            version, urn, implementation, services, service_types, api_versions, fields = self._delegate.get_version(self.requestCertificate())
            result = {}
            result['VERSION'] = version
            if urn:
                result['URN'] = urn
            if implementation:
                result['IMPLEMENTATION'] = implementation
            if services:
                result['SERVICES'] = services
            result['SERVICE_TYPES'] = service_types
            result['API_VERSIONS'] = api_versions
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return gapitools.form_error_return(logger, e)
        return gapitools.form_success_return(result)

    def lookup(self, _type, options):
        try:
            field_match = field_filter = None
            for option in options:
                if 'filter' in option:
                    field_filter = option.get('filter')
                elif 'match' in option:
                    field_match = option.get('match')
            result = self._delegate.lookup(_type, self.requestCertificate(), field_filter, field_match, options)
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

class GRegistryv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Clearinghouse API (v2). 
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
        "SERVICE_TYPE" : {
            "TYPE"    : "STRING",
            "DESC"    : "Name of service type (from Federation Registry get_version.TYPES)"},
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
        super(GRegistryv2DelegateBase, self).__init__()
    
    def get_version(self):
        """Overwrite this method in the actual delegate implementation.
        Return information about version and options 
          (e.g. filter, query, credential types) accepted by this service
        
        Arguments: None
        
        Return:
            get_version structure information as described above
       """
        raise GFedv2NotImplementedError("Method not implemented")
        
    def lookup(self, _type, client_cert, field_filter, field_match, options):
        """Overwrite this method in the actual delegate implementation.
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

        NB: This is an unprotected call, no client cert required."""
        raise GFedv2NotImplementedError("Method not implemented")

        
    def lookup_authorities_for_urns(self, client_cert, urns):
        """Overwrite this method in the actual delegate implementation.
        Lookup the authorities for a given URNs. There should be at most one (potentially none) per URN.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv2NotImplementedError("Method not implemented")
        
    def get_trust_roots(self, client_cert):
        """Overwrite this method in the actual delegate implementation.
        Return list of trust roots (certificates) associated with this CH.
        Often this is a concatenatation of the trust roots of the included authorities.
        Should return a list of strings.
        NB: This is an unprotected call, no client cert required."""
        raise GFedv2NotImplementedError("Method not implemented")


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
