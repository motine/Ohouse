import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('och1')

GCHv1DelegateBase = pm.getService('gchv1delegatebase')
gch_ex = pm.getService('gchv1exceptions')

VERSION = '0.1'

class OCH1Delegate(GCHv1DelegateBase):
    def get_version(self, client_cert):
        chrm = pm.getService('ochrm')
        fields = dict( (name.upper(), {"TYPE" : typ.upper()}) for (name, typ) in chrm.supplementary_fields().iteritems()) # convert the fields to the correct format
        return VERSION, fields

    def get_aggregates(self, client_cert, field_filter, field_match, options):
        chrm = pm.getService('ochrm')
        return self._match_and_filter(chrm.all_aggregates(), field_filter, field_match)
        
    def get_member_authorities(self, client_cert, field_filter, field_match, options):
        chrm = pm.getService('ochrm')
        return self._match_and_filter(chrm.all_member_authorities(), field_filter, field_match)

    def get_slice_authorities(self, client_cert, field_filter, field_match, options):
        chrm = pm.getService('ochrm')
        return self._match_and_filter(chrm.all_slice_authorities(), field_filter, field_match)

    def lookup_authorities_for_urns(self, client_cert, urns):
        chrm = pm.getService('ochrm')
        try:
            result = chrm.get_authory_mappings(urns)
        except ValueError as e:
            raise gch_ex.GCHv1ArgumentError(str(e))
        return result
        
    def get_trust_roots(self, client_cert):
        chrm = pm.getService('ochrm')
        return chrm.all_trusted_certs()
