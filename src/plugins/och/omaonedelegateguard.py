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
        original_field_filter = None # add MEMBER_URN if not present in the field_filter, so we have something to do authZ with
        if field_filter and not ("MEMBER_URN" in field_filter):
            original_field_filter = field_filter[:]
            field_filter.append("MEMBER_URN")

        result = super(OMA1DelegateGuard, self).lookup_private_member_info(client_cert, credentials, field_filter, field_match, options)

        # TODO refactor with above
        client_cert = geniutil.infer_client_cert(client_cert, credentials)
        try:
            trusted_cert_path = expand_amsoil_path('deploy/trusted') # TODO make config item out of it
            geniutil.verify_certificate(client_cert, trusted_cert_path)
            for info in result:
                geniutil.verify_credential(credentials, client_cert, info["MEMBER_URN"], trusted_cert_path, ('list',))
        except Exception as e:
            raise gch_ex.GCHv1AuthorizationError(str(e))

        if original_field_filter: # now remove the additional field again
            result = self._whitelist_fields(result, original_field_filter)

        return result
