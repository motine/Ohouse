import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('och1')

GMAv1DelegateBase = pm.getService('gmav1delegatebase')
gch_ex = pm.getService('gchv1exceptions')


class OMA1Delegate(GMAv1DelegateBase):
    VERSION = '0.1'
    SUPPLEMENTARY_FIELDS = {
        "ISLAND_NAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "OFELIA Island of the member",
            "CREATE" : "ALLOWED",
            "UPDATE" : True,
            "MATCH"   : True,
            "PROTECT" : "PUBLIC"
        }
    }

    def get_version(self):
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

    def lookup_public_member_info(self, field_filter, field_match, options):

        all_members = self.TEST_DATA # TODO get this from the database
        
        result = []
        # filter data, so only public member info is given out
        for member in all_members:
            reduced_member_info = {}
            for entry_key, entry_value in member.iteritems():
                if not entry_key in self.DATA_MAPPING: # skip the entry if there is no mapping
                    continue
                # figure out the spec for the entry
                mapped_entry_key = self.DATA_MAPPING[entry_key]
                entry_spec = None # find the specification for the entry
                if mapped_entry_key in self.DEFAULT_FIELDS:
                    entry_spec = self.DEFAULT_FIELDS[mapped_entry_key]
                if mapped_entry_key in self.SUPPLEMENTARY_FIELDS:
                    entry_spec = self.SUPPLEMENTARY_FIELDS[mapped_entry_key]
                if not entry_spec:
                    raise RuntimeError("Spec for field could not be found. The delegate programmer did miss something (%s)" % (mapped_entry_key,))
                # only copy the info fitting the level of PROTECT
                if entry_spec['PROTECT'] == 'PUBLIC':
                    reduced_member_info[mapped_entry_key] = entry_value
            result.append(reduced_member_info)
        return self._match_and_filter(result, field_filter, field_match)

    TEST_DATA = [
        {
            "urn" : "urn:publicid:IDN+eict:de+user+tom",
            "uuid" : "7ab95414-0e03-4007-91c0-fb771eeb523f",
            "first_name" : 'Tom',
            "last_name" : 'Jerry',
            "user_name" : 'tomtom',
            "email" : 'tom@example.com',
            "cert" : '<cert>..TOM..</cert>'
        }, {
            "urn" : "urn:publicid:IDN+eict:de+user+manfred",
            "uuid" : "0eaf6064-a731-4d5b-b627-01352abdbeb8",
            "first_name" : 'Manfred',
            "last_name" : 'Tester',
            "user_name" : 'manni',
            "email" : 'manni@freds.net',
            "cert" : '<cert>..MAN..</cert>'
        }]
    
    DATA_MAPPING =  { # maps database entries to the names returned to the client
        "urn" : "MEMBER_URN",
        "uuid" : "MEMBER_UID",
        "first_name" : 'MEMBER_FIRSTNAME',
        "last_name" : 'MEMBER_LASTNAME',
        "user_name" : 'MEMBER_USERNAME',
        "email" : 'MEMBER_EMAIL'}
