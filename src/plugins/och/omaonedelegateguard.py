from amsoil.config import expand_amsoil_path
import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('och1')

from omaonedelegate import OMA1Delegate
gch_ex = pm.getService('gchv1exceptions')

config = pm.getService('config')
geniutil = pm.getService('geniutil')

class OMA1DelegateGuard(OMA1Delegate):
    """Wraps the OMA1Delegate and performs authorization."""

    # no authentication, hence no overwrite
    # def lookup_public_member_info(self, client_cert, field_filter, field_match, options):

    def lookup_identifying_member_info(self, client_cert, credentials, field_filter, field_match, options):
        # TODO auth
        
        result = super(OMA1DelegateGuard, self).lookup_identifying_member_info(client_cert, credentials, field_filter, field_match, options)
        return result

    def lookup_private_member_info(self, client_cert, credentials, field_filter, field_match, options):
        result = super(OMA1DelegateGuard, self).lookup_private_member_info(client_cert, credentials, field_filter, field_match, options)

        # # TODO refactor with above
        # client_cert = geniutil.infer_client_cert(client_cert, credentials)
        # try:
        #     trusted_cert_path = expand_amsoil_path('deploy/trusted') # TODO make config item out of it
        #     geniutil.verify_certificate(client_cert, trusted_cert_path)
        #     for info in result:
        #         geniutil.verify_credential(credentials, client_cert, info["MEMBER_URN"], trusted_cert_path, ('list',))
        # except Exception as e:
        #     raise gch_ex.GCHv1AuthorizationError(str(e))
        # 
        return result
