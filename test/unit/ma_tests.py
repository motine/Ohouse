#!/usr/bin/env python

import unittest
from testtools import *

def ma_call(method_name, params=[], valid_user=True, verbose=True):
    key_path, cert_path = 'alice-key.pem', 'alice-cert.pem'
    if not valid_user:
        key_path, cert_path = 'malcom-key.pem', 'malcom-cert.pem'
    res = ssl_call(method_name, params, 'MA', key_path=key_path, cert_path=cert_path)
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
        except:
            warn("Error while trying to setup supplementary fields before starting tests")
        
    def test_get_version(self):
        code, value, output = ma_call('get_version')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        self.assertIn('VERSION', value)
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
                self.assertIn(fv["TYPE"], ["URN", "UID", "STRING", "DATETIME", "EMAIL", "KEY","BOOLEAN", "CREDENTIAL", "CERTIFICATE"])

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
    
     # TODO test if match attributes are rejected if match is not allowed by get_version
     # TODO make sure PROTECT attributes are not given out unless public

    def test_lookup_public_member_info(self):
        req_fields = ["MEMBER_URN", "MEMBER_UID", "MEMBER_USERNAME"]
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PUBLIC']
        self._check_lookup("lookup_public_member_info", "MEMBER_UID", req_fields)

    def test_lookup_identifying_member_info(self):
        req_fields = ["MEMBER_FIRSTNAME", "MEMBER_LASTNAME"]
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'IDENTIFYING']
        self._check_lookup("lookup_identifying_member_info", "MEMBER_EMAIL", req_fields, ["CREDENTIAL"])

    def test_lookup_private_member_info(self):
        req_fields = []
        req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PRIVATE']
        uniq_field = req_fields[0] if len(req_fields) > 0 else None
        self._check_lookup("lookup_private_member_info", uniq_field, req_fields, ['CREDENTIAL'])

    def test_bad_user_attempts(self):
        code, value, output = ma_call("lookup_public_member_info", [{}], valid_user=False)
        self.assertIn(code, [1,2]) # should throw any auth error
        code, value, output = ma_call("lookup_private_member_info", [["CREDENTIAL"], {}], valid_user=False)
        self.assertIn(code, [1,2]) # should throw any auth error

    def _check_lookup(self, method_name, unique_field_to_test_match_with, required_fields, credentials=None):
        if credentials:
            code, value, output = ma_call(method_name, [credentials, {}])
        else:
            code, value, output = ma_call(method_name, [{}])
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, list)
        for member_info in value:
            for req_str_field in required_fields:
                self.assertIn(req_str_field, member_info)
                self.assertIn(type(member_info[req_str_field]), [str, bool])
        if len(value) == 0:
            warn("No member info to test with (returned no records by %s)." % (method_name,))
        # test match
        if len(value) > 0:
            params = [{'match' : {unique_field_to_test_match_with : value[0][unique_field_to_test_match_with]}}]
            if credentials:
                params.insert(0, credentials)
            fcode, fvalue, foutput = ma_call(method_name, params)
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertEqual(len(fvalue), 1)
        # test filter
        if len(value) > 0:
            params = [{'filter' : [unique_field_to_test_match_with]}]
            if credentials:
                params.insert(0, credentials)
            fcode, fvalue, foutput = ma_call(method_name, params)
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertIsInstance(fvalue[0], dict)
            self.assertEqual(fvalue[0].keys(), [unique_field_to_test_match_with])
            self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change
        
if __name__ == '__main__':
    unittest.main(verbosity=0, exit=False)
    print_warnings()