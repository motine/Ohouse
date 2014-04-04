import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gregistryrpc')

xmlrpc = pm.getService('xmlrpc')

class GRegistryv2Handler(xmlrpc.Dispatcher):
    """
    Handle XML-RPC Federation Registry API calls.
    """

    def __init__(self):
        """
        Initialise logger and clear delegate.
        """
        super(GRegistryv2Handler, self).__init__(logger)
        self._api_tools = pm.getService('apitools')
        self._delegate = None

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
        Get details for this Federation Registry implementation.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.get_version()
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def lookup(self, type_, _, options):
        """
        Lookup objects with given type.

        Unwrap 'match' and 'filter' fields out of 'options'.

        Ignore credentials, as this is an unprotected call.

        Call delegate method and return result or exception.

        """
        try:
            match, filter_ = self._api_tools.fetch_match_and_filter(options)
            result = self._delegate.lookup(type_, match, filter_, options)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def lookup_authorities_for_urns(self, urns):
        """
        Lookup authorities for given URNs.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.lookup_authorities_for_urns(self.requestCertificate(), urns)
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

    def get_trust_roots(self):
        """
        Get trust roots for this Federation Registry.

        Call delegate method and return result or exception.

        """
        try:
            result = self._delegate.get_trust_roots(self.requestCertificate())
        except Exception as e:
            return self._api_tools.form_error_return(logger, e)
        return self._api_tools.form_success_return(result)

class GRegistryv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Clearinghouse API (v2).
    """

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

    def lookup(self, type_, _, options):
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

        Note: This is an unprotected call, no client cert required.

        Arguments:
           type: type of objects for which details are being requested
           options: What details to provide (filter options)
                   for which objects (match options)

        Return: List of dictionaries (indexed by object URN) with field/value pairs
          for each returned object

        """
        raise GFedv2NotImplementedError("Method not implemented")


    def lookup_authorities_for_urns(self, urns):
        """Overwrite this method in the actual delegate implementation.
        Lookup the authorities for a given URNs. There should be at most one (potentially none) per URN.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GFedv2NotImplementedError("Method not implemented")

    def get_trust_roots(self):
        """Overwrite this method in the actual delegate implementation.
        Return list of trust roots (certificates) associated with this CH.
        Often this is a concatenatation of the trust roots of the included authorities.
        Should return a list of strings.
        NB: This is an unprotected call, no client cert required."""
        raise GFedv2NotImplementedError("Method not implemented")
