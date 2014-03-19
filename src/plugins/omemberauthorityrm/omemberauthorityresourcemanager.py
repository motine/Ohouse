import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('omemberauthorityrm')

geniutil = pm.getService('geniutil')

from omemberauthorityexceptions import *
import omemberauthorityutil

class OMemberAuthorityResourceManager(object):

    SUPPLEMENTARY_FIELDS = {
        "_OFELIA_MEMBER_AFFILIATION" : {
            "OBJECT" : "MEMBER",
            "TYPE"   : "STRING",
            "DESC"   : "Organization the member belongs to",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"  : True,
            "PROTECT": "IDENTIFYING"
        },
        "_OFELIA_ISLAND_NAME": {
            "OBJECT" : "MEMBER",
            "TYPE"   : "STRING",
            "DESC"   : "Home island of the member",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"  : True,
            "PROTECT": "PUBLIC"
        },
        "_OFELIA_MEMBER_X509_CERTIFICATE" : {
            "OBJECT" : "MEMBER",
            "TYPE"   : "CERTIFICATE",
            "DESC"   : "X509 Certificate",
            "CREATE" : "ALLOWED",
            "UPDATE" : False,
            "MATCH"  : False,
            "PROTECT": "PUBLIC"
        },
        "_OFELIA_MEMBER_X509_PRIVATE_KEY" : {
            "OBJECT" : "MEMBER",
            "TYPE"   : "KEY",
            "DESC"   : "Private key for the X509 Certificate",
            "CREATE" : "ALLOWED",
            "UPDATE" : False,
            "MATCH"  : False,
            "PROTECT": "PRIVATE"
        },
        "_OFELIA_MEMBER_ENABLED" : {
            "OBJECT" : "MEMBER",
            "TYPE"   : "BOOLEAN",
            "DESC"   : "If the user is allowed to perform actions",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"  : True,
            "PROTECT": "PUBLIC"
        }
    }

        # ---- Member Service Methods
    MEMBER_DEFAULT_FIELDS = {
        "MEMBER_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of given member",
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_UID" : {
            "TYPE"    : "UID",
            "DESC"    : "UID (unique within authority) of member",
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_FIRSTNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "First name of member",
            "MATCH"   : True,
            "PROTECT" : "IDENTIFYING"},
        "MEMBER_LASTNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Last name of member",
            "MATCH"   : True,
            "PROTECT" : "IDENTIFYING"},
        "MEMBER_USERNAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Username of user",
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"},
        "MEMBER_EMAIL" : {
            "TYPE"    : "STRING",
            "DESC"    : "Email of user",
            "MATCH"   : False,
            "PROTECT" : "IDENTIFYING"}}

    SUPPORTED_SERVICES = ['MEMBER','KEY']

    SUPPORTED_CREDENTIAL_TYPES = [{"type" : "SFA", "version" : 1}]

    def __init__(self):
        super(OMemberAuthorityResourceManager, self).__init__()

    def lookup_member(self, client_cert, credentials):
        c_urn, c_uuid, c_email = geniutil.extract_certificate_info(geniutil.infer_client_cert(client_cert, credentials))
        members = self.MEMBER_TEST_DATA # TODO get this from the database
        members = self._map_field_names(members)        
        whitelist = ['MEMBER_URN']
        #Decide implementation specific details
        if True:
            whitelist = whitelist + self._member_field_names_for_protect('PRIVATE')
        if True:
            whitelist = whitelist + self._member_field_names_for_protect('IDENTIFYING')
        if True:
            whitelist = whitelist + self._member_field_names_for_protect('PUBLIC')
        members = self._whitelist_fields(members, whitelist)
        return members

    def lookup_key(self, client_cert, credentials):
        c_urn, c_uuid, c_email = geniutil.extract_certificate_info(geniutil.infer_client_cert(client_cert, credentials))
        keys = self.KEY_TEST_DATA # TODO get this from the database
        return keys

    def create_key(self, client_cert, credentials, options):
        key_id = hash(options.key_public)

        #insert {'type':'key', 'key_member':options.key_member, 'key_id':options.key_member, 'key_type':options.key_type, 
        #    'key_public':options.key_public, 'key_private':options.key_options, 'key_description':options.key_description}
        
        return key_id

    def update_key(self, client_cert, credentials, options):
        #update {'type':key, 'key_id':options.key_id} {'key_description' : options.key_description}
        pass

    def delete_key(self, client_cert, credentials, options):
        #delete {'type':key, 'key_id':options.key_id}
        pass

    def urn(self):
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        return 'urn:publicid:IDN+' + hostname + '+authority+ma'

    def implementation(self):
        additional_info = pm.getAdditionalInfo('omemberauthorityrm')
        if len(additional_info) > 0:
            return {'code_version' : str(additional_info['version'])} 
        else: 
            return None

    def services(self):
        return self.SUPPORTED_SERVICES

    def api_versions(self):
        config = pm.getService('config')
        hostname = config.get('flask.hostname')
        port = str(config.get('flask.app_port'))
        endpoints = pm.getEndpoint('type', 'ma')
        return omemberauthorityutil.form_api_versions(hostname, port, endpoints)

    def supplementary_fields(self):
        """Returns a list of custom fields with the associated type. e.g. {"FIELD_NAME" : "STRING", "SECOND" : "UID"}"""
        fields = {}
        for fname, f in self.SUPPLEMENTARY_FIELDS.iteritems():
            fields[fname] = {
                "TYPE" : f["TYPE"],
                "PROTECT" : f["PROTECT"]
            }
            if "CREATE" in f:
                fields[fname]["CREATE"] = f["CREATE"]
            if "MATCH" in f:
                fields[fname]["MATCH"] = f["MATCH"]
            if "UPDATE" in f:
                fields[fname]["UPDATE"] = f["UPDATE"]
        return fields

    def credential_types(self):
        return self.SUPPORTED_CREDENTIAL_TYPES

    # -- Helper methods
    def _member_field_names_for_protect(self, protect):
        """
        Returns all keys (e.g. MEMEBER_URN) which have the given value for protect (e.g. PUBLIC).
        Both the keys in DEFAULT_FIELDS (with object 'MEMBER') and SUPPLEMENTARY_FIELDS are considered.
        """
        result = []
        fields = self.MEMBER_DEFAULT_FIELDS.copy()
        fields.update((k,v) for k,v in self.SUPPLEMENTARY_FIELDS.iteritems() if (v['OBJECT'] == 'MEMBER'))
        for (name, spec) in fields.iteritems():
            if spec['PROTECT'] == protect:
                result.append(name)
        return result

    def _map_field_names(self, members):
        """
        Convertes the internal representation to the GENI field names (e.g. attribute name urn to MEMBER_URN).
        Unmapped entries are eliminated.
        """
        result = []
        for member in members:
            mapped_info = {}
            for entry_key, entry_value in member.iteritems():
                if not entry_key in self.DATA_MAPPING: # skip the entry if there is no mapping
                    continue
                mapped_info[self.DATA_MAPPING[entry_key]] = entry_value
            result.append(mapped_info)
        return result

    def _whitelist_fields(self, members, whitelist):
        """Reduces members' attributes to only have field names which are in whitelist.
        {members} A list of dicts.
        {whitelist} A list of strings."""
        result = []
        for member in members:
            reduced_member_info = {}
            for entry_key, entry_value in member.iteritems():
                # only copy the info fitting the level of PROTECT
                if entry_key in whitelist:
                    reduced_member_info[entry_key] = entry_value
            result.append(reduced_member_info)
        return result

        # ---- helper methods
    def _match_and_filter_and_to_dict(self, list_of_dicts, key_field, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter_and_to_dict(list_of_dicts, key_field, field_filter, field_match)
    
    def _match_and_filter(self, list_of_dicts, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter(list_of_dicts, field_filter, field_match)
    
    def _filter_fields(self, d, field_filter):
        """see documentation in gapitools"""
        return gapitools.filter_fields(d, field_filter)

    def _does_match_fields(self, d, field_match):
        """see documentation in gapitools"""
        return gapitools.does_match_fields(d, field_match)

    MEMBER_TEST_DATA = [
        {
            "urn" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice",
            "uuid" : "7ab95414-0e03-4007-91c0-fb771e11111",
            "first_name" : 'Alice',
            "last_name" : 'Merry',
            "user_name" : 'alice',  # e.g. to be used as linux login name, needs to be unique
            "email" : 'alice@example.com',
            "affiliation" : 'OFELIA PO',
            "island" : 'Berlin, Germany',
            "x509_cert" : '<cert>..ALICE..</cert>',
            "x509_priv_key_str" : '', # None if user generated key; save None in the database but offer a xxx_str method which gives out an empty string to comply with XML-RPC
            "ssh_pub_key" : 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5',
            "ssh_priv_key_str" : 'bsbs', # None
            "enabled" : True
        }, {
            "urn" : "urn:publicid:IDN+eict:de+user+tom",
            "uuid" : "7ab95414-0e03-4007-91c0-fb771eeb523f",
            "first_name" : 'Tom',
            "last_name" : 'Jerry',
            "user_name" : 'tomtom',  # e.g. to be used as linux login name, needs to be unique
            "email" : 'tom@example.com',
            "affiliation" : 'EICT',
            "island" : 'Berlin, Germany',
            "x509_cert" : '<cert>..TOM..</cert>',
            "x509_priv_key_str" : 'sss', # None if user generated key; save None in the database but offer a xxx_str method which gives out an empty string to comply with XML-RPC
            "ssh_pub_key" : 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5',
            "ssh_priv_key_str" : 'asd', # None
            "enabled" : True
        }, {
            "urn" : "urn:publicid:IDN+eict:de+user+manfred",
            "uuid" : "0eaf6064-a731-4d5b-b627-01352abdbeb8",
            "first_name" : 'Manfred',
            "last_name" : 'Tester',
            "user_name" : 'manni',
            "affiliation" : 'EICT',
            "email" : 'manni@freds.net',
            "island" : 'Spain',
            "x509_cert" : '<cert>..MAN..</cert>',
            "x509_priv_key_str" : '...', # str value if key generated by the CH
            "ssh_pub_key" : 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5',
            "ssh_priv_key_str" : 'some key',
            "enabled" : True
        }]

    KEY_DATA_MAPPING =  { # maps database entries to the names returned to the client
        "urn" : "KEY_MEMBER",
        "ssh_pub_key" : "KEY_PUBLIC",
        "ssh_priv_key_str" : "KEY_PRIVATE"
        }
    
    DATA_MAPPING =  { # maps database entries to the names returned to the client
        "urn" : "MEMBER_URN",
        "uuid" : "MEMBER_UID",
        "first_name" : 'MEMBER_FIRSTNAME',
        "last_name" : 'MEMBER_LASTNAME',
        "user_name" : 'MEMBER_USERNAME',
        "email" : 'MEMBER_EMAIL',
        "affiliation" : '_OFELIA_MEMBER_AFFILIATION',
        "island" : '_OFELIA_ISLAND_NAME',
        "x509_cert" : '_OFELIA_MEMBER_X509_CERTIFICATE',
        "x509_priv_key_str" : '_OFELIA_MEMBER_X509_PRIVATE_KEY',
        "enabled" : '_OFELIA_MEMBER_ENABLED'
        }