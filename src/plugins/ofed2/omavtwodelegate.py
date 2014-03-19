import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GMAv2DelegateBase = pm.getService('gmav2delegatebase')
gfed_ex = pm.getService('gfedv2exceptions')

config = pm.getService('config')
geniutil = pm.getService('geniutil')

VERSION = '2'

class OMAv2Delegate(GMAv2DelegateBase):
    
    def get_version(self):
        ma_rm = pm.getService('omemberauthorityrm')
        return VERSION, ma_rm.urn(), ma_rm.implementation(), ma_rm.services(), ma_rm.credential_types(), ma_rm.api_versions(), ma_rm.supplementary_fields()

    def create(self, _type, credentials, options):
        ma_rm = pm.getService('omemberauthorityrm')
        if (_type=='KEY'):
            pass

    def update(self, _type, urn, credentials, options):
        ma_rm = pm.getService('omemberauthorityrm')
        if (_type=='MEMBER'):
            pass
        elif (_type=='KEY'):
            pass

    def delete(self, _type, urn, credentials, options):
        ma_rm = pm.getService('omemberauthorityrm')
        if (_type=='KEY'):
            pass

    def lookup(self, _type, certificate, credentials, field_match, field_filter, options):
        ma_rm = pm.getService('omemberauthorityrm')
        print field_match
        if (_type=='MEMBER'):
            return self._match_and_filter_and_to_dict(ma_rm.lookup_member(certificate, credentials), "MEMBER_URN", field_filter, field_match)
        elif (_type=='KEY'):
            return self._match_and_filtert(ma_rm.lookup_key(certificate, credentials), field_filter, field_match)

    # ---- Member Service Methods
    def get_credentials(self, member_urn, credentials, options):
        ma_rm = pm.getService('omemberauthorityrm')
