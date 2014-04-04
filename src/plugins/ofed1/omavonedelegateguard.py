from amsoil.config import expand_amsoil_path
import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

from omavonedelegate import OMAv1Delegate
gfed_ex = pm.getService('gfedv1exceptions')

config = pm.getService('config')
geniutil = pm.getService('geniutil')

class OMAv1DelegateGuard(OMAv1Delegate):
    """Wraps the OMAv1Delegate and performs authorization."""

    # no authentication, hence no overwrite
    # def lookup_public_member_info(self, client_cert, field_filter, field_match, options):

    def lookup_identifying_member_info(self, client_cert, credentials, field_filter, field_match, options):
        result = super(OMAv1DelegateGuard, self).lookup_identifying_member_info(client_cert, credentials, field_filter, field_match, options)
        self._authorize_dict_list(client_cert, credentials, result, options)
        return result

    def lookup_private_member_info(self, client_cert, credentials, field_filter, field_match, options):
        result = super(OMAv1DelegateGuard, self).lookup_private_member_info(client_cert, credentials, field_filter, field_match, options)
        self._authorize_dict_list(client_cert, credentials, result, options)
        return result
    
    def _authorize_dict_list(self, client_cert, credentials, result, options):
        client_cert = geniutil.infer_client_cert(client_cert, credentials)
        try:
            trusted_cert_path = expand_amsoil_path(config.get("ofed.cert_root"))
            geniutil.verify_certificate(client_cert, trusted_cert_path)
            # TODO remove this (only for testing)
            # BEGING REMOVE
            client_urn, client_uuid, client_email = geniutil.extract_certificate_info(client_cert)
            client_auth, client_type, client_name = geniutil.decode_urn(client_urn)
            if not client_name == "admin": # only test if the name is not admin
            # END REMOVE
                for urn, info in result.iteritems():
                    geniutil.verify_credential(credentials, client_cert, urn, trusted_cert_path, ('list',))
        except Exception as e:
            raise gfed_ex.GFedv1AuthorizationError(str(e))
