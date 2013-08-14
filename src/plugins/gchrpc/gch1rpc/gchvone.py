import traceback
import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gch1rpc')

# from amsoil.config import ROOT_PATH
# from amsoil.config import expand_amsoil_path

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GCHv1Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GCHv1Handler, self).__init__(logger)
        self._delegate = None
    
    @serviceinterface
    def setDelegate(self, geniv3delegate):
        self._delegate = geniv3delegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

    def get_version(self):
        """Delegates the call and unwraps the needed parameter."""
        try:
            version, fields = self._delegate.get_version()
            result = {}
            result['VERSION'] = version
            if fields:
                result["FIELDS"] = fields
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def get_aggregates(self, options):
        """Delegates the call and unwraps the needed parameter."""
        try:
            field_filter = options.pop('filter') if ('filter' in options) else None
            field_match = options.pop('match') if ('match' in options) else None
            result = self._delegate.get_aggregates(field_filter, field_match, options)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def get_member_authorities(self, options):
        """Delegates the call and unwraps the needed parameter."""
        pass
    def get_slice_authorities(self, options):
        """Delegates the call and unwraps the needed parameter."""
        pass
    def lookup_authorities_for_urns(self, urns):
        """Delegates the call and unwraps the needed parameter."""
        pass
    def get_trust_roots(self):
        """Delegates the call and unwraps the needed parameter."""
        pass

    # ---- helper methods
    def _errorReturn(self, e):
        """Assembles a GENI compliant return result for faulty methods."""
        if not isinstance(e, GCHv1BaseError): # convert unknown errors into GCHv1ServerError
            e = GCHv1ServerError(str(e))
        # do some logging
        logger.error(e)
        logger.error(traceback.format_exc())
        return { 'code' : e.code, 'output' : str(e) }
        
    def _successReturn(self, result):
        """Assembles a GENI compliant return result for successful methods."""
        return { 'code' : 0, 'value' : result, 'output' : None }



class GCHv1DelegateBase(object):
    """
    {match}, {filter} and {fields} semantics are explained in the GENI CH API document.
    """
    
    def __init__(self):
        super(GCHv1DelegateBase, self).__init__()
    
    def get_version(self):
        """Overwrite this method in the actual delegate implementation.
        Provide a structure detailing the version information as well as details of accepted options s for CH API calls.
        NB: This is an unprotected call, no client cert required.
        
        This method shall return
        - a version string (e.g. 1.0.3)
        - None or a dictionary of custom CH fields (e.g. {"TYPE" : "URN"}, for more info and available types, please see the API spec)
        """
        raise GCHv1NotImplementedError("Method not implemented")
        
    def get_aggregates(self, field_filter, field_match, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all aggregates associated with the Federation.
        Should return a list of dicts (filtered and matched).
        NB: This is an unprotected call, no client cert required."""
        raise GCHv1NotImplementedError("Method not implemented")

    def get_member_authorities(self, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all MA's associated with the Federation.
        NB: This is an unprotected call, no client cert required."""
        raise GCHv1NotImplementedError("Method not implemented")
        
    def get_slice_authorities(self, options):
        """Overwrite this method in the actual delegate implementation.
        Return information about all SA's associated with the Federation
        NB: This is an unprotected call, no client cert required."""
        raise GCHv1NotImplementedError("Method not implemented")
        
    def lookup_authorities_for_urns(self, urns):
        """Overwrite this method in the actual delegate implementation.
        Lookup the authorities for a given URNs. There should be at most one (potentially none) per URN.
        NB: This is an unprotected call, no client cert required."""
        raise GCHv1NotImplementedError("Method not implemented")
        
    def get_trust_roots(self):
        """Overwrite this method in the actual delegate implementation.
        Return list of trust roots (certificates) associated with this CH. Often this is a concatenatation of the trust roots of the included authorities.
        NB: This is an unprotected call, no client cert required."""
        raise GCHv1NotImplementedError("Method not implemented")


    # -- helper methods
    def _match_and_filter(self, list_of_dicts, field_filter, field_match):
        """Takes a list of dicts and applies the given filter and matches the results."""
        return [self._filter_fields(d, field_filter) for d in list_of_dicts if self._does_match_fields(d, field_match)]
    
    def _filter_fields(self, d, field_filter):
        if not field_filter:
            return d
        result = {}
        for f in field_filter:
            result[f] = d[f]
        return result
    
    def _does_match_fields(self, d, field_match):
        """
        field_match may look like: { 'must_be' : 'this', 'and_any_of_' : ['tho', 'se']}
        """
        if not field_match:
            return True
        for mk, mv in field_match.iteritems(): # each matches must be fulfilled
            val = d[mk]
            if isinstance(mv, list): # any of those values (OR)
                found_any = False;
                for mvv in mv:
                    if val == mvv:
                        found_any = True
                if not found_any:
                    return False
            else: # or explicitly this one
                if not val == mv:
                    return False
        return True
        
