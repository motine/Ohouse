import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GRegistryv2DelegateBase = pm.getService('gregistryv2delegatebase')
gfed_ex = pm.getService('apiexceptionsv2')

VERSION = '2'

class ORegistryv2Delegate(GRegistryv2DelegateBase):
    """
    Implements Federation Registry methods.
    """

    def __init__(self):
        """
        Get plugins for use in other class methods.

        Checks consistency of 'SERVICES' fields defined in configuration
        (config.json).
        """
        self._federation_registry_resource_manager = pm.getService('oregistryrm')
        self._delegate_tools = pm.getService('delegatetools')
        for service in self._delegate_tools.get_registry()['SERVICES']:
            self._delegate_tools.object_consistency_check('SERVICE', service)

    def get_version(self):
        """
        Get implementation details from resource manager. Supplement these with
        additional details specific to the delegate.
        """
        version = self._delegate_tools.get_version(self._federation_registry_resource_manager)
        version['VERSION'] = VERSION
        version['FIELDS'] =  self._delegate_tools.get_supplementary_fields(['SERVICE'])
        return version

    def lookup(self, type_, match, filter_, options):
        """
        Depending on the object type defined in the request, lookup this object
        using the resource manager.
        """
        if (type_=='SERVICE'):
             return self._delegate_tools.match_and_filter(self._federation_registry_resource_manager.lookup_services(), filter_, match)
        else:
            raise gfed_ex.GFedv2NotImplementedError("No create method found for object type: " + str(type_))

    def lookup_authorities_for_urns(self, client_cert, urns):
        """
        Return authorities for a given URN using the resource manager.
        """
        try:
            result =  self._federation_registry_resource_manager.get_authory_mappings(urns)
        except ValueError as e:
            raise gfed_ex.GFedv2ArgumentError(str(e))
        return result

    def get_trust_roots(self, client_cert):
        """
        Return trust roots from resource manager.
        """
        return  self._federation_registry_resource_manager.all_trusted_certs()
