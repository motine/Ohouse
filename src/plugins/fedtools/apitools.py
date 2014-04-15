from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm

import traceback
from apiexceptions import GFedv2BaseError, GFedv2ServerError

class APITools(object):
    """
    Common tools used to implement an RPC interface.

    Includes the registration and lookup of RPC endpoints.
    """

    def __init__(self):
        self._database = pm.getService('mongodb')

    # --- fetch filter and match fields from options
    @staticmethod
    @serviceinterface
    def fetch_match_and_filter(options):
        field_match = options.get('match', {})
        field_filter = options.get('filter', {})
        return field_match, field_filter

    @staticmethod
    @serviceinterface
    def pop_fields(options):
        return options.pop('fields',{})

    # --- deal with the GENI CH API returns
    @staticmethod
    @serviceinterface
    def form_error_return(logger, e):
        """Assembles a GENI compliant return result for faulty methods."""
        if not isinstance(e, GFedv2BaseError): # convert unknown errors into GFedv2ServerError
            e = GFedv2ServerError(str(e))
        # do some logging
        logger.error(e)
        logger.error(traceback.format_exc())
        return { 'code' : e.code, 'output' : str(e) }

    @staticmethod
    @serviceinterface
    def form_success_return(result):
        """Assembles a GENI compliant return result for successful methods."""
        return { 'code' : 0, 'value' : result, 'output' : None }


    # # --- helpers for filtering/selecting stuff
    # @staticmethod
    # def match_and_filter_and_to_dict(list_of_dicts, key_field, field_filter, field_match):
    #     """Takes a list of dicts applies the {field_filter} and {field_match} (see match_and_filter).
    #     Then converts the list into a dict by using the {key_field} as key.
    #     E.g. match_and_filter_and_to_dict([{"x":1,"y":5}, {"x":2,"y":6}], "x", ...) results in {1:{"y":5}, 2:{"y":6}}
    #     """
    #     if field_filter and not key_field in field_filter:
    #         field_filter += [key_field]
    #     matched_and_filtered = match_and_filter(list_of_dicts, field_filter, field_match)

    #     for d in matched_and_filtered:
    #         if not key_field in d:
    #             raise ValueError("Can not convert to dict because the key_field name (%s) is not in the dictionary (%s)" % (key_field, d))
    #     return { d[key_field] : dict(filter(lambda (k,v): (k != key_field), d.iteritems())) for d in matched_and_filtered}


    @serviceinterface
    def get_endpoints(self, **kwargs):
        """
        Return all endpoints matching given arguments.

        For example get_endpoints(type='sa'), get_endpoints(url='/ma/2').
        """
        return self._database.lookup('endpoint', kwargs)

    @serviceinterface
    def register_endpoint(self, **kwargs):
        """
        Register a new endpoint.

        For example register_endpoint(type='sa', url='/ma/2')
        """
        self._database.update('endpoint', kwargs, kwargs, upsert=True)

