#!/usr/bin/env python

import unittest
import pprint
from testtools import *

COLORS={"reset":"\x1b[00m",
    "blue":   "\x1b[01;34m",
    "cyan":   "\x1b[01;36m",
    "green":  "\x1b[01;32m",
    "red":    "\x1b[01;05;37;41m"}

def ch_call(method_name, params=[]):
    res = ssl_call(method_name, params, 'CH')
    # output stuff
    print COLORS["blue"],
    print "--> %s(%s)" % (method_name, params)
    print COLORS["cyan"],
    pprint.pprint(res, indent=4, width=20)
    print COLORS["reset"]
    # ...
    return res.get('code', None), res.get('value', None), res.get('output', None)

class TestGCHv1(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_version(self):
        code, value, output = ch_call('get_version')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        self.assertIn('VERSION', value)
        if 'FIELDS' in value:
            self.assertIsInstance(value['FIELDS'], dict)
            for fk, fv in value['FIELDS'].iteritems():
                self.assertIsInstance(fk, str)
                self.assertIsInstance(fv, dict)
                self.assertIn("TYPE", fv)
                self.assertIn(fv["TYPE"], ["URN", "UID", "STRING", "DATETIME", "EMAIL", "KEY","BOOLEAN", "CREDENTIAL", "CERTIFICATE"])
                # if "CREATE" in fv:
                #     self.assertIn(fv["CREATE"], ["REQUIRED", "ALLOWED", "NOT ALLOWED"])
                # if "UPDATE" in fv:
                #     self.assertIn(fv["UPDATE"], [True, False])
                
    def test_get_aggregates(self):
        code, value, output = ch_call('get_aggregates', [{}])
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, list)
        for agg in value:
            for req_str_field in ['SERVICE_URN', 'SERVICE_URL', 'SERVICE_CERT', 'SERVICE_NAME', 'SERVICE_DESCRIPTION']:
                self.assertIn(req_str_field, agg)
                self.assertIsInstance(agg[req_str_field], str)
        # test match
        if len(value) > 0:
            fcode, fvalue, foutput = ch_call('get_aggregates', [{'match' : {'SERVICE_URN' : value[0]['SERVICE_URN']}}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertEqual(len(fvalue), 1)
        # test filter
        if len(value) > 0:
            fcode, fvalue, foutput = ch_call('get_aggregates', [{'filter' : ['SERVICE_URN']}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertIsInstance(fvalue[0], dict)
            self.assertEqual(fvalue[0].keys(), ['SERVICE_URN'])
            self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change
        
if __name__ == '__main__':
    unittest.main(verbosity=0)
