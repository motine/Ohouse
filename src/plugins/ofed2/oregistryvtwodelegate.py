import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GRegistryv2DelegateBase = pm.getService('gregistryv2delegatebase')
gfed_ex = pm.getService('gfedv2exceptions')

VERSION = '2'

class ORegistryv2Delegate(GRegistryv2DelegateBase):
    def get_version(self, client_cert):
        reg_rm = pm.getService('oregistryrm')
        return VERSION, reg_rm.urn(), reg_rm.implementation(), reg_rm.services(),  reg_rm.service_types(), reg_rm.api_versions(), reg_rm.supplementary_fields()

    def lookup(self, _type, client_cert, field_filter, field_match, options):
        reg_rm = pm.getService('oregistryrm')
        if (_type=='SLICE_AUTHORITY'):
             return self._match_and_filter(reg_rm.all_slice_authorities(), field_filter, field_match)
        elif(_type=='MEMBER_AUTHORITY'):
            return self._match_and_filter(reg_rm.all_member_authorities(), field_filter, field_match)
        elif(_type=='AGGREGATE_MANAGER'):
            return self._match_and_filter(reg_rm.all_aggregates(), field_filter, field_match)

    def lookup_authorities_for_urns(self, client_cert, urns):
        reg_rm = pm.getService('oregistryrm')
        try:
            result = reg_rm.get_authory_mappings(urns)
        except ValueError as e:
            raise gfed_ex.GFedv2ArgumentError(str(e))
        return result
        
    def get_trust_roots(self, client_cert):
        reg_rm = pm.getService('oregistryrm')
        return reg_rm.all_trusted_certs()