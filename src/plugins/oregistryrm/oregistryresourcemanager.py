import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('oregistryrm')

from oregistryexceptions import *
import oregistryutil

class ORegistryResourceManager(object):
    """
    """
    AGGREGATE_SERVICE_TYPE = 'AGGREGATE_MANAGER'
    SA_SERVICE_TYPE = 'SLICE_AUTHORITY'
    MA_SERVICE_TYPE = 'MEMBER_AUTHORITY'

    SUPPORTED_SERVICES = ['SERVICE']

    def __init__(self):
        super(ORegistryResourceManager, self).__init__()
        self.consistency_check()


    def consistency_check(self):
        # try to catch the most common syntax errors in the config
        self._check_raise("registry" in oregistryutil.CONFIG, "No CH element found.")
        self._check_raise("supplementary_fields" in oregistryutil.CONFIG["registry"], "No 'supplementary_fields' found in 'CH' found (it can be empty but must be there).")
        self._check_raise("services" in oregistryutil.CONFIG["registry"], "No 'services' found in 'CH'.")
        self._check_raise("trust_roots" in oregistryutil.CONFIG["registry"], "No 'trust_roots' found in 'CH'.")
        
        for service in oregistryutil.CONFIG["registry"]["services"]:
            self._check_raise("service_url"  in service, "No 'service_url' found in 'services'.")
            self._check_raise("service_cert" in service, "No 'service_cert' found in 'services'.")
            self._check_raise("service_name" in service, "No 'service_name' found in 'services'.")
            self._check_raise("service_description" in service, "No 'service_description' found in 'services'.")
            self._check_raise("service_urn"  in service, "No 'service_urn' found in 'services'.")
            self._check_raise("service_type"         in service, "No 'type' found in 'services'.")
            self._check_raise(service["service_type"] in [self.AGGREGATE_SERVICE_TYPE, self.SA_SERVICE_TYPE, self.MA_SERVICE_TYPE], "A service type should be either %s, %s or %s" % (self.AGGREGATE_SERVICE_TYPE, self.SA_SERVICE_TYPE, self.MA_SERVICE_TYPE))
            for field in oregistryutil.CONFIG["registry"]["supplementary_fields"]:
                self._check_raise(field in service, "Supplementary field not found in service (%s)." % (field,))
    
        for tr in oregistryutil.CONFIG["registry"]["trust_roots"]:
            self._check_raise(type(tr) in [str, unicode], "All 'trust_roots' entries should be strings.")   

    def urn(self):
        try:
            return oregistryutil.CONFIG["registry"]["urn"]
        except:
            return None

    def implementation(self):
        additional_info = pm.getAdditionalInfo('oregistryrm')
        if len(additional_info) > 0:
            return {'code_version' : str(additional_info['version'])} 
        else: 
            return None

    def services(self):
        return self.SUPPORTED_SERVICES

    def service_types(self):
        service_types = set()
        for e in oregistryutil.CONFIG["registry"]["services"]:
            service_types.add(e['service_type'])
        return list(service_types)

    def api_versions(self):
        base_url = 'https://example.com/xmlrpc'
        endpoints = pm.getEndpoint('type', 'reg')
        api_versions = {}
        for key, endpoint in endpoints.iteritems():
            api_versions[endpoint.get('version')] = base_url + endpoint.get('url')
        return api_versions
            
    def supplementary_fields(self):
        """Returns a list of custom fields with the associated type. e.g. {"FIELD_NAME" : "STRING", "SECOND" : "UID"}"""
        return dict( (name.upper(), {"TYPE" : typ.upper()}) for (name, typ) in oregistryutil.CONFIG["registry"]["supplementary_fields"].iteritems()) 
        
    def all_aggregates(self):
        return self._uppercase_keys_in_list([e for e in oregistryutil.CONFIG["registry"]["services"] if (e['service_type']==self.AGGREGATE_SERVICE_TYPE)])
        
    def all_member_authorities(self):
        return self._uppercase_keys_in_list([e for e in oregistryutil.CONFIG["registry"]["services"] if (e['service_type']==self.MA_SERVICE_TYPE)])
        
    def all_slice_authorities(self):
        return self._uppercase_keys_in_list([e for e in oregistryutil.CONFIG["registry"]["services"] if (e['service_type']==self.SA_SERVICE_TYPE)])
        
    def all_trusted_certs(self):
        certs = oregistryutil.CONFIG["registry"]["trust_roots"]
        # subsitute magic markers
        if "INFER_SAs" in certs:
            certs.remove("INFER_SAs")
            for s in self.all_slice_authorities():
                certs.append(s['SERVICE_CERT'])
        if "INFER_MAs" in certs:
            certs.remove("INFER_MAs")
            for s in self.all_member_authorities():
                certs.append(s['SERVICE_CERT'])
        return certs
    
    def get_authory_mappings(self, urns):
        geniutil = pm.getService('geniutil')
        if not isinstance(urns, list):
            raise ValueError("Please give a _list_ of URNs")
        result = {}

        for urn in urns:
            authority, typ, name = geniutil.decode_urn(urn)
            service = None
            if (typ == "slice"):
                service = self._find_service(self.SA_SERVICE_TYPE, authority)
            if (typ == "user"):
                service = self._find_service(self.MA_SERVICE_TYPE, authority)
            if (typ == "sliver"):
                service = self._find_service(self.AGGREGATE_SERVICE_TYPE, authority)

            if service:
                result[urn] = service['service_url']
        return result
    
    def _find_service(self, typ, authority):
        """returns the first service dictionary matching the {typ}e and {urn}. None if none is found."""
        geniutil = pm.getService('geniutil')
        for service in oregistryutil.CONFIG['registry']['services']:
            sauth, styp, sname = geniutil.decode_urn(service['service_urn'])
            if (service['service_type'] == typ) and (sauth == authority):
                return service
        return None
    
    def _uppercase_keys_in_list(self, list_of_dicts):
        return [self._uppercase_keys_in_dict(e) for e in list_of_dicts]
        
    def _uppercase_keys_in_dict(self, adict):
        return dict( (k.upper(), v) for (k, v) in adict.iteritems() )
    
    def _check_raise(self, condition, message):
        if not condition:
            raise RegistryMalformedConfigFile(oregistryutil.config_path(), message)