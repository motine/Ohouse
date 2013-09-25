import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GRegistryv1DelegateBase = pm.getService('gregistryv1delegatebase')
gfed_ex = pm.getService('gfedv1exceptions')

VERSION = '0.1'

class ORegistryv1Delegate(GRegistryv1DelegateBase):
    def get_version(self, client_cert):
        regrm = pm.getService('oregistryrm')
        fields = dict( (name.upper(), {"TYPE" : typ.upper()}) for (name, typ) in regrm.supplementary_fields().iteritems()) # convert the fields to the correct format
        return VERSION, fields

    def lookup_aggregates(self, client_cert, field_filter, field_match, options):
        regrm = pm.getService('oregistryrm')
        return self._match_and_filter(regrm.all_aggregates(), field_filter, field_match)
        
    def lookup_member_authorities(self, client_cert, field_filter, field_match, options):
        regrm = pm.getService('oregistryrm')
        return self._match_and_filter(regrm.all_member_authorities(), field_filter, field_match)

    def lookup_slice_authorities(self, client_cert, field_filter, field_match, options):
        regrm = pm.getService('oregistryrm')
        return self._match_and_filter(regrm.all_slice_authorities(), field_filter, field_match)

    def lookup_authorities_for_urns(self, client_cert, urns):
        regrm = pm.getService('oregistryrm')
        try:
            result = regrm.get_authory_mappings(urns)
        except ValueError as e:
            raise gfed_ex.GFedv1ArgumentError(str(e))
        return result
        
    def get_trust_roots(self, client_cert):
        regrm = pm.getService('oregistryrm')
        return regrm.all_trusted_certs()