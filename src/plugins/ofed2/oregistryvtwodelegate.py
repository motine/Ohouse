import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GRegistryv2DelegateBase = pm.getService('gregistryv2delegatebase')
gfed_ex = pm.getService('gfedv2exceptions')

VERSION = '2'

class ORegistryv2Delegate(GRegistryv2DelegateBase):
    def get_version(self, client_cert):
        regrm = pm.getService('oregistryrm')
        fields = dict( (name.upper(), {"TYPE" : typ.upper()}) for (name, typ) in regrm.supplementary_fields().iteritems()) # convert the fields to the correct format
        return VERSION, regrm.urn(), regrm.implementation(), regrm.services(),  regrm.service_types(), regrm.api_versions(), fields

    def lookup(self, _type, client_cert, field_filter, field_match, options):
        regrm = pm.getService('oregistryrm')
        if (_type=='SLICE_AUTHORITY'):
             return self._match_and_filter(regrm.all_slice_authorities(), field_filter, field_match)
        elif(_type=='MEMBER_AUTHORITY'):
            return self._match_and_filter(regrm.all_member_authorities(), field_filter, field_match)
        elif(_type=='AGGREGATE_MANAGER'):
            return self._match_and_filter(regrm.all_aggregates(), field_filter, field_match)

    def lookup_authorities_for_urns(self, client_cert, urns):
        regrm = pm.getService('oregistryrm')
        try:
            result = regrm.get_authory_mappings(urns)
        except ValueError as e:
            raise gfed_ex.GFedv2ArgumentError(str(e))
        return result
        
    def get_trust_roots(self, client_cert):
        regrm = pm.getService('oregistryrm')
        return regrm.all_trusted_certs()