#!/usr/bin/env python

import unittest
from testtools import *
import sys

arg = None

def reg_call(method_name, params=[], user_name='alice'):
    if arg in ['-v', '--verbose']:
        verbose = True
    else:
        verbose = False
    return api_call(method_name, 'reg/2', params=params, user_name=user_name, verbose=verbose)

class TestGRegistryv2(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_version(self):
        code, value, output = reg_call('get_version')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        self.assertIn('VERSION', value)
        if 'FIELDS' in value:
            self.assertIsInstance(value['FIELDS'], dict)
            for fk, fv in value['FIELDS'].iteritems():
                self.assertIsInstance(fk, str)
                self.assertEqual(fk[0], '_')
                self.assertIsInstance(fv, dict)
                self.assertIn("TYPE", fv)
                self.assertIn(fv["TYPE"], ["URN", "UID", "STRING", "DATETIME", "EMAIL", "KEY","BOOLEAN", "CREDENTIAL", "CERTIFICATE"])
                # if "CREATE" in fv:
                #     self.assertIn(fv["CREATE"], ["REQUIRED", "ALLOWED", "NOT ALLOWED"])
                # if "UPDATE" in fv:
                #     self.assertIn(fv["UPDATE"], [True, False])
        else:
            warn("No supplementary fields to test with.")

    def test_get_trust_roots(self):
        code, value, output = reg_call('get_trust_roots')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, list)
        if len(value) == 0:
            warn("No trust roots returned.")
        for tr in value:
            self.assertIsInstance(tr, str)

    def test_lookup_authorities_for_urns(self):
        # slice, user, sliver, project

        # dynamically create urns from get_aggregates, get_member_authorities, get_slice_authorities
        _, aggs, _ = reg_call('lookup', ['SERVICE', {}, {}])
        _, mas, _ = reg_call('lookup', ['SERVICE',  {}, {}])
        _, sas, _ = reg_call('lookup', ['SERVICE',  {}, {}])

        mappings = {} # contains {test_urn_to_send : service_url, ... }
        if (len(aggs) == 0):
            warn("No aggregates to test with.")
        else:
            mappings[aggs[0]['SERVICE_URN'].replace('authority+am', 'sliver+vm77')] = aggs[0]['SERVICE_URL']
        if (len(mas) == 0):
            warn("No MAs to test with.")
        else:
            mappings[mas[0]['SERVICE_URN'].replace('authority+ma', 'user+tomtom')] = mas[0]['SERVICE_URL']
        if (len(sas) == 0):
            warn("No SAs to test with.")
        else:
            mappings[sas[0]['SERVICE_URN'].replace('authority+sa', 'slice+pizzaslice')] = sas[0]['SERVICE_URL']
        code, value, output = reg_call('lookup_authorities_for_urns', [[urn for (urn, _) in mappings.iteritems()]])
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        for (res_urn, res_url) in value.iteritems():
            self.assertIn(res_urn, mappings)
            self.assertEqual(mappings[res_urn], res_url)

    def test_lookup(self):
        self._check_a_listing('lookup', 'SERVICE', 'aggregate')
        self._check_a_listing('lookup', 'SERVICE', 'member authority')
        self._check_a_listing('lookup', 'SERVICE', 'slice authority')

    def _check_a_listing(self, method_name, type_, entity_name):
        code, value, output = reg_call(method_name, [type_, {}, {}])
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, list)
        for agg in value:
            for req_str_field in ['SERVICE_URN', 'SERVICE_URL', 'SERVICE_CERT', 'SERVICE_NAME', 'SERVICE_DESCRIPTION']:
                self.assertIn(req_str_field, agg)
                self.assertIsInstance(agg[req_str_field], str)
        # test match
        if len(value) == 0:
            warn("No %s to test with" % (entity_name,))
        if len(value) > 0:
            fcode, fvalue, foutput = reg_call(method_name,  [type_, {}, {'match' : {'SERVICE_URL' : value[0]['SERVICE_URL']}}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertEqual(len(fvalue), 1)
        # test filter
        if len(value) > 0:
            fcode, fvalue, foutput = reg_call(method_name, [type_,  {}, {'filter' : ['SERVICE_URL']}])
            self.assertEqual(fcode, 0) # no error
            self.assertIsInstance(fvalue, list)
            self.assertIsInstance(fvalue[0], dict)
            self.assertEqual(fvalue[0].keys(), ['SERVICE_URL'])
            self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change

if __name__ == '__main__':
    if len(sys.argv) == 2:
        arg = sys.argv[1]
    del sys.argv[1:]
    unittest.main(verbosity=0, exit=True)
    print_warnings()
