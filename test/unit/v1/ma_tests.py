#!/usr/bin/env python

import unittest
from testtools import *

def ma_call(method_name, params=[], user_name='alice', verbose=True):
    key_path, cert_path = "%s-key.pem" % (user_name,), "%s-cert.pem" % (user_name,)
    res = ssl_call(method_name, params, 'ma/1', key_path=key_path, cert_path=cert_path)
    if verbose:
        print_call(method_name, params, res)
    return res.get('code', None), res.get('value', None), res.get('output', None)

class TestGMAv1(unittest.TestCase):

    @classmethod
    def setUpClass(klass):
        # try to get custom fields before we start the tests
        klass.sup_fields = []
        try:
            code, value, output = ma_call('get_version', verbose=False)
            klass.sup_fields = value['FIELDS']
            klass.has_key_service = ('KEY' in value['SERVICES'])
        except Exception as e:
            warn(["Error while trying to setup supplementary fields before starting tests (%s)" % (repr(e),)])
        
    def test_get_version(self):
        code, value, output = ma_call('get_version')
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
                self.assertIn(fv["TYPE"], ["URN", "UID", "STRING", "DATETIME", "EMAIL", "KEY", "BOOLEAN", "CREDENTIAL", "CERTIFICATE"])
    
                if "CREATE" in fv:
                    self.assertIn(fv["CREATE"], ["REQUIRED", "ALLOWED", "NOT ALLOWED"])
                if "MATCH" in fv:
                    self.assertIsInstance(fv["MATCH"], bool)
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
        req_fields = ["MEMBER_FIRSTNAME", "MEMBER_LASTNAME", "MEMBER_EMAIL"]
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'IDENTIFYING']
        self._check_lookup("lookup_identifying_member_info", req_fields, True)
    
    def test_lookup_private_member_info(self):
        req_fields = []
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PRIVATE']
        self._check_lookup("lookup_private_member_info", req_fields, True)
    
    def test_filter_with_auth(self):
        for meth in ["lookup_identifying_member_info", "lookup_private_member_info"]:
            code, value, output = ma_call(meth, [self._credential_list("alice"), {"match" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
            self.assertEqual(code, 0)
            code, value, output = ma_call(meth, [self._credential_list("malcom"), {}])
            self.assertIn(code, [1,2])
            code, value, output = ma_call(meth, [self._credential_list("malcom"), {"match" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
            self.assertIn(code, [1,2])

    def _check_lookup(self, method_name, required_fields, use_creds=False):
        if use_creds:
            code, value, output = ma_call(method_name, [self._credential_list("admin"), {}], user_name="admin")
        else:
            code, value, output = ma_call(method_name, [{}], user_name="admin")
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        for member_urn, member_info in value.iteritems():
            for req_str_field in required_fields:
                self.assertIn(req_str_field, member_info)
                self.assertIn(type(member_info[req_str_field]), [str, bool])
        if len(value) == 0:
            warn("No member info to test with (returned no records by %s)." % (method_name,))
        # test match
        if len(value) > 0:
            params = [{'match' : {"MEMBER_URN" : value.keys()[0]}}]
            if use_creds:
                params.insert(0, self._credential_list("admin"))
            fcode, fvalue, foutput = ma_call(method_name, params, user_name="admin")
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
            fcode, fvalue, foutput = ma_call(method_name, params, user_name="admin")
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
        """Returns the _user_ credential for malcom."""
        return [{"SFA" : get_creds_file_contents('malcom-cred.xml')}]
    def _credential_list(self, user_name):
        """Returns the _user_ credential for the given user_name."""
        return [{"SFA" : get_creds_file_contents('%s-cred.xml' % (user_name,))}]

if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
    print_warnings()
