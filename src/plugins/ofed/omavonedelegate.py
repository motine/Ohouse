import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('ofed')

GMAv1DelegateBase = pm.getService('gmav1delegatebase')
gch_ex = pm.getService('gfedv1exceptions')


class OMAv1Delegate(GMAv1DelegateBase):
    VERSION = '0.1'
    SUPPLEMENTARY_FIELDS = {
        "MEMBER_AFFILIATION" : {
            "TYPE"    : "STRING",
            "DESC"    : "Organization the member belongs to",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : True,
            "PROTECT" : "IDENTIFYING"
        },
        "ISLAND_NAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Home island of the member (island of OFELIA)",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"
        },
        "MEMBER_X509_CERTIFICATE" : {
            "TYPE"    : "CERTIFICATE",
            "DESC"    : "X509 Certificate",
            "CREATE" : "ALLOWED",
            "UPDATE" : False,
            "MATCH"   : False,
            "PROTECT" : "PUBLIC"
        },
        "MEMBER_X509_PRIVATE_KEY" : {
            "TYPE"    : "KEY",
            "DESC"    : "Private key for the X509 Certificate",
            "CREATE" : "ALLOWED",
            "UPDATE" : False,
            "MATCH"   : False,
            "PROTECT" : "PRIVATE"
        },
        "MEMBER_SSH_PUBLIC_KEY" : {
            "TYPE"    : "KEY",
            "DESC"    : "Public portion of the SSH key",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"
        },
        "MEMBER_SSH_PRIVATE_KEY" : {
            "TYPE"    : "KEY",
            "DESC"    : "Public portion of the SSH key",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : False,
            "PROTECT" : "PRIVATE"
        },
        "MEMBER_ENABLED" : {
            "TYPE"    : "BOOLEAN",
            "DESC"    : "If the user is allowed to perform actions (on the CH or elsewhere)",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"
        }
    }

    def get_version(self, client_cert):
        # no auth necessary
        certs = {"SFA": "1"}
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
        return self.VERSION, certs, fields

    def lookup_public_member_info(self, client_cert, field_filter, field_match, options):
        # no auth necessary
        members = self.TEST_DATA # TODO get this from the database
        members = self._map_field_names(members)
        members = self._whitelist_fields(members, self._field_names_for_protect('PUBLIC')) # filter data, so only public/identifying/private member info is given out
        return self._match_and_filter_and_to_dict(members, "MEMBER_URN", field_filter, field_match)

    def lookup_identifying_member_info(self, client_cert, credentials, field_filter, field_match, options):
        # TODO get the data from the database
        members = self.TEST_DATA
        members = self._map_field_names(members)
        members = self._whitelist_fields(members, self._field_names_for_protect('IDENTIFYING') + ['MEMBER_URN'])
        return self._match_and_filter_and_to_dict(members, "MEMBER_URN", field_filter, field_match)

    def lookup_private_member_info(self, client_cert, credentials, field_filter, field_match, options):
        c_urn, c_uuid, c_email = geniutil.extract_certificate_info(geniutil.infer_client_cert(client_cert, credentials))
        members = self.TEST_DATA # TODO get this from the database
        members = self._map_field_names(members)
        members = self._whitelist_fields(members, self._field_names_for_protect('PRIVATE') + ['MEMBER_URN'])
        return self._match_and_filter_and_to_dict(members, "MEMBER_URN", field_filter, field_match)

    # -- Helper methods
    def _field_names_for_protect(self, protect):
        """
        Returns all keys (e.g. MEMEBER_URN) which have the given value for protect (e.g. PUBLIC).
        Both the keys in DEFAULT_FIELDS and SUPPLEMENTARY_FIELDS are considered.
        """
        result = []
        fields = self.DEFAULT_FIELDS.copy()
        fields.update(self.SUPPLEMENTARY_FIELDS)
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

    TEST_DATA = [
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
    
    DATA_MAPPING =  { # maps database entries to the names returned to the client
        "urn" : "MEMBER_URN",
        "uuid" : "MEMBER_UID",
        "first_name" : 'MEMBER_FIRSTNAME',
        "last_name" : 'MEMBER_LASTNAME',
        "user_name" : 'MEMBER_USERNAME',
        "email" : 'MEMBER_EMAIL',
        "affiliation" : 'MEMBER_AFFILIATION',
        "island" : 'ISLAND_NAME',
        "ssh_pub_key" : 'MEMBER_SSH_PUBLIC_KEY',
        "ssh_priv_key_str" : 'MEMBER_SSH_PRIVATE_KEY',
        "x509_cert" : 'MEMBER_X509_CERTIFICATE',
        "x509_priv_key_str" : 'MEMBER_X509_PRIVATE_KEY',
        "enabled" : 'MEMBER_ENABLED'
        }