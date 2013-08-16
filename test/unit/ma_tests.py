#!/usr/bin/env python

import unittest
from testtools import *

def ma_call(method_name, params=[]):
    res = ssl_call(method_name, params, 'MA')
    print_call(method_name, params, res)
    return res.get('code', None), res.get('value', None), res.get('output', None)

class TestGMAv1(unittest.TestCase):

    def setUp(self):
        pass

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
    
    def test_lookup_public_member_info(self):
        method_name = "lookup_public_member_info"
        code, value, output = ma_call(method_name, [{}])
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, list)
        for member_info in value:
            for req_str_field in ["MEMBER_URN", "MEMBER_UID", "MEMBER_USERNAME"]: # "MEMBER_URN", "MEMBER_UID", "MEMBER_FIRSTNAME", "MEMBER_LASTNAME", "MEMBER_USERNAME", "MEMBER_EMAIL"
                self.assertIn(req_str_field, member_info)
                self.assertIsInstance(member_info[req_str_field], str)
        if len(value) == 0:
            warn("No member info to test with.")
        # test match
        if len(value) > 0:
            fcode, fvalue, foutput = ma_call(method_name, [{'match' : {'MEMBER_UID' : value[0]['MEMBER_UID']}}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertEqual(len(fvalue), 1)
        # test filter
        if len(value) > 0:
            fcode, fvalue, foutput = ma_call(method_name, [{'filter' : ['MEMBER_UID']}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertIsInstance(fvalue[0], dict)
            self.assertEqual(fvalue[0].keys(), ['MEMBER_UID'])
            self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change
            

    
         # TODO test if match attributes are rejected if match is not allowed by get_version
         # TODO make sure PROTECT attributes are not given out unless public
        
if __name__ == '__main__':
    unittest.main(verbosity=0)