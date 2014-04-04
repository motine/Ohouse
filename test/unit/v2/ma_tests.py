#!/usr/bin/env python

import unittest
from testtools import *

def ma_call(method_name, params=[], user_name='alice', verbose=False):
    key_path, cert_path = "%s-key.pem" % (user_name,), "%s-cert.pem" % (user_name,)
    res = ssl_call(method_name, params, 'ma/2', key_path=key_path, cert_path=cert_path)
    if verbose:
        print_call(method_name, params, res)
    return res.get('code', None), res.get('value', None), res.get('output', None)

class TestGMAv2(unittest.TestCase):

    @classmethod
    def setUpClass(klass):
        # try to get custom fields before we start the tests
        klass.sup_fields = []
        try:
            code, value, output = ma_call('get_version', verbose=True)
            klass.sup_fields = value['FIELDS']
            klass.has_key_service = ('KEY' in value['SERVICES'])
        except Exception as e:
            warn(["Error while trying to setup supplementary fields before starting tests (%s)" % (repr(e),)])

    def test_get_version(self):
        """
        Test 'get_version' method.

        Check result for various valid/required fields.
        """
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
        self.assertIsInstance(creds, list)
        self.assertTrue(len(creds) > 0)
        for cred in creds:
            self.assertIsInstance(cred['type'], str)
            self.assertIsInstance(cred['version'], int)
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

    # def test_lookup(self):
    #      code, value, output = ma_call('lookup', ['MEMBER', self._credential_list("alice"), {"match" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])

    # def test_lookup_public_member_info(self):
    #     req_fields = ["MEMBER_UID", "MEMBER_USERNAME"] # MEMBER_URN is implicit, since it is used to index the returned dict
    #     req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PUBLIC']
    #     self._check_lookup("lookup", req_fields)

    # def test_lookup_identifying_member_info(self):
    #     req_fields = ["MEMBER_FIRSTNAME", "MEMBER_LASTNAME", "MEMBER_EMAIL"]
    #     req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'IDENTIFYING']
    #     self._check_lookup("lookup", req_fields, True)

    # def test_lookup_private_member_info(self):
    #     req_fields = []
    #     req_fields += [fn for (fn, fv) in self.__class__.sup_fields.iteritems() if fv['PROTECT'] == 'PRIVATE']
    #     self._check_lookup("lookup", req_fields, True)

    # def test_filter_with_auth(self):
    #     code, value, output = ma_call('lookup', ['MEMBER', self._credential_list("alice"), {"match" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
    #     self.assertEqual(code, 0)
    #     code, value, output = ma_call('lookup', ['MEMBER', self._credential_list("malcom"), {}])
    #     self.assertIn(code, [1,2])
    #     code, value, output = ma_call('lookup', ['MEMBER', self._credential_list("malcom"), {"match" : {"MEMBER_URN" : "urn:publicid:IDN+test:fp7-ofelia:eu+user+alice"}}])
    #     self.assertIn(code, [1,2])

    # def _check_lookup(self, method_name, required_fields, use_creds=False):
    #     if use_creds:
    #         code, value, output = ma_call(method_name, ['MEMBER', self._credential_list("admin"), {}], user_name="admin")
    #     else:
    #         code, value, output = ma_call(method_name, ['MEMBER', {}, {}], user_name="admin")
    #     self.assertEqual(code, 0) # no error
    #     self.assertIsInstance(value, dict)
    #     for member_urn, member_info in value.iteritems():
    #         for req_str_field in required_fields:
    #             self.assertIn(req_str_field, member_info)
    #             self.assertIn(type(member_info[req_str_field]), [str, bool])
    #     if len(value) == 0:
    #         warn("No member info to test with (returned no records by %s)." % (method_name,))
    #     # test match
    #     if len(value) > 0:
    #         params = ['MEMBER', {}, {'match' : {"MEMBER_URN" : value.keys()[0]}}]
    #         if use_creds:
    #             params = ['MEMBER', self._credential_list("admin"), {'match' : {"MEMBER_URN" : value.keys()[0]}}]
    #         else:
    #             params = ['MEMBER', {}, {'match' : {"MEMBER_URN" : value.keys()[0]}}]
    #         fcode, fvalue, foutput = ma_call(method_name, params, user_name="admin")
    #         self.assertEqual(fcode, 0) # no error
    #         self.assertIsInstance(fvalue.keys()[0], str)
    #         self.assertIsInstance(fvalue.values()[0], dict)
    #         self.assertEqual(len(fvalue), 1)
    #     # test filter
    #     if len(value) > 0:
    #         filter_key = value.values()[0].keys()[0]
    #          # take any field which was sent before
    #         if use_creds:
    #             params = ['MEMBER', self._credential_list("admin"), {'filter' : [filter_key]}]
    #         else:
    #             params = ['MEMBER', {}, {'filter' : [filter_key]}]

    #         fcode, fvalue, foutput = ma_call(method_name, params, user_name="admin")
    #         self.assertEqual(fcode, 0) # no error
    #         self.assertIsInstance(fvalue, dict)
    #         self.assertIsInstance(fvalue.keys()[0], str)
    #         self.assertIsInstance(fvalue.values()[0], dict)
    #         self.assertEqual(fvalue.values()[0].keys(), [filter_key])
    #         self.assertEqual(len(value), len(fvalue)) # the number of returned aggregates should not change

    def test_malformed_field(self):
        """
        Test type checking by passing a malformed field ('KEY_MEMBER' as a boolean)
        during creation.
        """
        create_data = {'KEY_MEMBER':True, 'KEY_TYPE':'rsa-ssh', 'KEY_DESCRIPTION':'SSH key for user Arlene Brown.', 'KEY_PUBLIC':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5'}
        self._test_create(create_data, 'KEY', 'KEY_ID', 3)

    def test_create_unauthorized_field(self):
        """
        Test creation rules by passing an unauthorized field ('KEY_ID') during creation.
        """
        create_data = {'KEY_ID' : '1', 'KEY_MEMBER':'urn:publicid:IDN+mych+user+abrown', 'KEY_TYPE':'rsa-ssh', 'KEY_DESCRIPTION':'SSH key for user Arlene Brown.', 'KEY_PUBLIC':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5'}
        self._test_create(create_data, 'KEY', 'KEY_ID', 3)

    def test_update_unauthorized_field(self):
        """
        Test update rules by passing an unauthorized field ('KEY_TYPE') during creation.
        """
        create_data = {'KEY_MEMBER':'urn:publicid:IDN+mych+user+abrown', 'KEY_TYPE':'rsa-ssh', 'KEY_DESCRIPTION':'SSH key for user Arlene Brown.', 'KEY_PUBLIC':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5'}
        urn = self._test_create(create_data, 'KEY', 'KEY_ID', 0)
        update_data = {'KEY_TYPE' : 'UNAUTHORIZED_UPDATE'}
        self._test_update(urn, update_data, 'KEY', 'KEY_ID', 3)

    def test_member(self):
        """
        Test object type 'MEMBER' methods:

        Member creation methods are out of Federation Service API scope. As such,
        there is no concrete method to test add test data, and therefore no way
        to test member methods ('lookup', 'update').
        """
        pass

    def test_key(self):
        """
        Test object type 'KEY' methods: create, lookup, update and delete.
        """
        create_data = {'KEY_MEMBER':'urn:publicid:IDN+mych+user+abrown', 'KEY_TYPE':'rsa-ssh', 'KEY_DESCRIPTION':'SSH key for user Arlene Brown.', 'KEY_PUBLIC':'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDhEds1KZkBCX9e91wN4ADs1+dGEm1wUYIe2WfDW3MwLkxwsiFvHAeD7uKUOOGXAZLevTaXWRuinkFaEu9hXfmnG46R2yyxgtq3zNQP+a7mPCbYV8x9LLQtGHXD9A19300WdsSmBlFvM6cTVWXeSnRSQq1LL2vbp0GlJk/UvqOoAEOEBMeQgQL4h1Bd4tMb8b2+FceFa43vDkHVy9QaVWjIVeCMqmYoR0A8MRI2Xm52KJ+XbyamtGWwyx817BSUurrVFc2levWHnz69GK9QuZWNL9LihkkMQoWRrKfr4lf5rbXCyRoUjZ+hTxxL0oEfjfXiaeinmJEMN5gudQ8oi6Y5'}
        urn = self._test_create(create_data, 'KEY', 'KEY_ID', 0)
        update_data = {'KEY_DESCRIPTION':'SSH key for user A. Brown.'}
        self._test_update(urn, update_data, 'KEY', 'KEY_ID', 0)
        self._test_delete(urn, 'KEY', 'KEY_ID', 0)

    def _test_create(self, fields, object_type, expected_urn, expected_code):
        """
        Helper method to test object creation.
        """
        code, value, output = ma_call('create', [object_type, self._credential_list("admin"), {'fields' : fields}], user_name="admin")
        self.assertEqual(code, expected_code)
        if code is 0:
            self.assertIsInstance(value, dict)
            for field_key, field_value in fields.iteritems():
                self.assertEqual(value.get(field_key), field_value)
            self.assertIn(expected_urn, value)
            urn = value.get(expected_urn)
            self.assertIsInstance(urn, str)
            return urn

    def _test_update(self, urn, fields, object_type, expected_urn, expected_code):
        """
        Helper method to test object update.
        """
        code, value, output = ma_call('update', [object_type, urn, self._credential_list("admin"), {'fields' : fields}], user_name="admin")
        self.assertEqual(code, expected_code)
        if code is 0:
            self.assertIsNone(value)
            result = self._test_lookup({expected_urn : urn}, None, object_type, 1, 0)
            for field_key, field_value in fields.iteritems():
                self.assertEqual(result[urn].get(field_key), field_value)

    def _test_lookup(self, match, _filter, object_type, expected_length, expected_code):
        """
        Helper method to test object lookup.
        """
        options = {}
        if match:
            options['match'] = match
        if _filter:
            options['filter'] = _filter
        code, value, output = ma_call('lookup', [object_type, self._credential_list("admin"), options], user_name="admin")
        self.assertEqual(code, expected_code)
        if expected_length:
            self.assertEqual(len(value), expected_length)
        return value

    def _test_delete(self, urn, object_type, expected_urn, expected_code):
        """
        Helper method to test object deletion.
        """
        code, value, output = ma_call('delete', [object_type, urn, self._credential_list("admin"), {}], user_name="admin")
        self.assertEqual(code, expected_code)
        self.assertIsNone(value)
        self._test_lookup({expected_urn : urn}, None, object_type, None, 0)

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
