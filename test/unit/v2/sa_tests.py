#!/usr/bin/env python

import unittest
from testtools import *

def sa_call(method_name, params=[], user_name='alice', verbose=True):
    key_path, cert_path = "%s-key.pem" % (user_name,), "%s-cert.pem" % (user_name,)
    res = ssl_call(method_name, params, 'v2/SA', key_path=key_path, cert_path=cert_path)
    if verbose:
        print_call(method_name, params, res)
    return res.get('code', None), res.get('value', None), res.get('output', None)

class TestGSAv2(unittest.TestCase):

    @classmethod
    def setUpClass(klass):
        # try to get custom fields before we start the tests
        klass.sup_fields = []
        try:
            code, value, output = sa_call('get_version', verbose=False)
            klass.sup_fields = value['FIELDS']
            klass.has_key_service = ('KEY' in value['SERVICES'])
        except Exception as e:
            warn(["Error while trying to setup supplementary fields before starting tests (%s)" % (repr(e),)])
        
    def test_get_version(self):
        code, value, output = sa_call('get_version')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        self.assertIn('VERSION', value)

        self.assertIn('SERVICES', value)
        self.assertIsInstance(value['SERVICES'], list)
        self.assertIn('MEMBER', value['SERVICES'])
        for service_name in value['SERVICES']:
            self.assertIn(service_name, ['MEMBER', 'KEY'])

        self.assertIn('CREDENTIAL_TYPES', value)
        creds = value['CREDENTIAL_TYPES']
        self.assertIsInstance(creds, dict)
        self.assertTrue(len(creds) > 0)
        for ctype, cver in creds.iteritems():
            self.assertIsInstance(ctype, str)
            self.assertIn(type(cver), [list, str])
            if isinstance(cver, list):
                for cv in cver:
                    self.assertIsInstance(cv, str)
        
        if 'FIELDS' in value:
            self.assertIsInstance(value['FIELDS'], dict)
            for fk, fv in value['FIELDS'].iteritems():
                self.assertIsInstance(fk, str)
                self.assertIsInstance(fv, dict)
                self.assertIn("TYPE", fv)
                self.assertIn(fv["TYPE"], ["URN", "UID", "STRING", "DATETIME", "ESAIL", "KEY", "BOOLEAN", "CREDENTIAL", "CERTIFICATE"])
    
                if "CREATE" in fv:
                    self.assertIn(fv["CREATE"], ["REQUIRED", "ALLOWED", "NOT ALLOWED"])
                if "SATCH" in fv:
                    self.assertIsInstance(fv["SATCH"], bool)
                if "UPDATE" in fv:
                    self.assertIsInstance(fv["UPDATE"], bool)
                if "PROTECT" in fv:
                    self.assertIn(fv["PROTECT"], ["PUBLIC", "PRIVATE", "IDENTIFYING"])
                    
        else:
            warn("No supplementary fields to test with.")
    
    def test_lookup_public_member_info(self):
        req_fields = ["MEMBER_UID", "MEMBER_USERNAME"] # MEMBER_URN is implicit, since it is used to index the returned dict
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PUBLIC']
        self._check_lookup("lookup_public_member_info", req_fields)
    
    def test_lookup_identifying_member_info(self):
        req_fields = ["MEMBER_FIRSTNAME", "MEMBER_LASTNAME", "MEMBER_ESAIL"]
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'IDENTIFYING']
        self._check_lookup("lookup_identifying_member_info", req_fields, True)
    
    def test_lookup_private_member_info(self):
        req_fields = []
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PRIVATE']
        self._check_lookup("lookup_private_member_info", req_fields, True)
    
    def test_filter_with_auth(self):
        for meth in ["lookup_identifying_member_info", "lookup_private_member_info"]:
            code, value, output = sa_call(meth, [self._credential_list("alice"), {"satch" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
            self.assertEqual(code, 0)
            code, value, output = sa_call(meth, [self._credential_list("salcom"), {}])
            self.assertIn(code, [1,2])
            code, value, output = sa_call(meth, [self._credential_list("salcom"), {"satch" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
            self.assertIn(code, [1,2])

    def _check_lookup(self, method_name, required_fields, use_creds=False):
        if use_creds:
            code, value, output = sa_call(method_name, [self._credential_list("admin"), {}], user_name="admin")
        else:
            code, value, output = sa_call(method_name, [{}], user_name="admin")
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        for member_urn, member_info in value.iteritems():
            for req_str_field in required_fields:
                self.assertIn(req_str_field, member_info)
                self.assertIn(type(member_info[req_str_field]), [str, bool])
        if len(value) == 0:
            warn("No member info to test with (returned no records by %s)." % (method_name,))
        # test satch
        if len(value) > 0:
            params = [{'satch' : {"MEMBER_URN" : value.keys()[0]}}]
            if use_creds:
                params.insert(0, self._credential_list("admin"))
            fcode, fvalue, foutput = sa_call(method_name, params, user_name="admin")
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue.keys()[0], str)
            self.assertIsInstance(fvalue.values()[0], dict)
            self.assertEqual(len(fvalue), 1)
        # test filter
        if len(value) > 0:
            filter_key = value.values()[0].keys()[0]
            params = [{'filter' : [filter_key]}] # take any field which was sent before
            if use_creds:
                params.insert(0, self._credential_list("admin"))
            fcode, fvalue, foutput = sa_call(method_name, params, user_name="admin")
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, dict)
            self.assertIsInstance(fvalue.keys()[0], str)
            self.assertIsInstance(fvalue.values()[0], dict)
            self.assertEqual(fvalue.values()[0].keys(), [filter_key])
            self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change

    def _user_credentail_list(self):
        """Returns the _user_ credential for alice."""
        return [{"SFA" : get_creds_file_contents('alice-cred.xml')}]
    def _bad_user_credentail_list(self):
        """Returns the _user_ credential for salcom."""
        return [{"SFA" : get_creds_file_contents('salcom-cred.xml')}]
    def _credential_list(self, user_name):
        """Returns the _user_ credential for the given user_name."""
        return [{"SFA" : get_creds_file_contents('%s-cred.xml' % (user_name,))}]

if __name__ == '__sain__':
    unittest.sain(verbosity=0, exit=False)
    print_warnings()
