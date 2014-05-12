#!/usr/bin/env python

import unittest
from testtools import *
import sys

arg = None

def sa_call(method_name, params=[], user_name='alice'):
    if arg in ['-v', '--verbose']:
        verbose = True
    else:
        verbose = False
    return api_call(method_name, 'sa/2', params=params, user_name=user_name, verbose=verbose)

def _remove_key(dct, val):
       copy = dct.copy()
       del copy[val]
       return copy

class TestGSAv2(unittest.TestCase):

    @classmethod
    def setUpClass(klass):
        # try to get custom fields before we start the tests
        klass.sup_fields = []
        try:
            code, value, output = sa_call('get_version')
            klass.sup_fields = value['FIELDS']
            klass.has_key_service = ('KEY' in value['SERVICES'])
        except Exception as e:
            warn(["Error while trying to setup supplementary fields before starting tests (%s)" % (repr(e),)])
        pass

    def test_get_version(self):
        """
        Test 'get_version' method.

        Check result for various valid/required fields.
        """
        code, value, output = sa_call('get_version')
        self.assertEqual(code, 0) # no error
        self.assertIsInstance(value, dict)
        self.assertIn('VERSION', value)
        self.assertIn('SERVICES', value)
        self.assertIsInstance(value['SERVICES'], list)
        self.assertIn('SLICE', value['SERVICES'])
        for service_name in value['SERVICES']:
            self.assertIn(service_name, ['SLICE','SLICE_MEMBER', 'SLIVER_INFO', 'PROJECT', 'PROJECT_MEMBER'])
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

    def test_malformed_field(self):
        """
        Test type checking by passing a malformed field ('KEY_MEMBER' as a boolean)
        during creation.
        """
        create_data = {'SLICE_NAME':True, 'SLICE_DESCRIPTION' : 'My Malformed Slice', 'SLICE_PROJECT_URN' : 'urn:publicid:IDN+this_sa+project+myproject'}
        self._test_create(create_data, 'SLICE', 'SLICE_URN', 3)

        lookup_data = {'SLICE_PROJECT_URN': 'urn:publicid:IDN+this_sa+project+myproject'}
        self.assertEqual(self._test_lookup(lookup_data,None,'SLICE',0), {})

    def test_invalid_slice_name(self):
        """
        This test is intended to test the validity of the slice_name upon creation.
        """
        invalid_charachters = ['_','!',"@",'#','$','%','^','&','*','(',')','+']
        invalid_sliceNames = ['invalid%sslicename' %c for c in invalid_charachters] +['-invalidslicename']

        for invalid_sliceName in invalid_sliceNames:
            create_data = {'SLICE_NAME': invalid_sliceName,
                           'SLICE_DESCRIPTION': 'My Malformed Slice',
                           'SLICE_PROJECT_URN': 'urn:publicid:IDN+this_sa+project+myproject'}
            self._test_create(create_data, 'SLICE', 'SLICE_URN',3)

            #Asserting to make sure the invalid slice name was not created
            lookup_data = {'SLICE_PROJECT_URN': 'urn:publicid:IDN+this_sa+project+myproject'}
            self.assertEqual(self._test_lookup(lookup_data,None,'SLICE',0), {})


    def test_create_unauthorized_field(self):
        """
        Test creation rules by passing an unauthorized field     ('KEY_ID') during creation.
        """
        create_data = {'SLICE_EXPIRED' : True, 'SLICE_NAME':'UNAUTHORIZED_CREATION',
                       'SLICE_DESCRIPTION' : 'My Unauthorized Slice',
                       'SLICE_PROJECT_URN' : 'urn:publicid:IDN+this_sa+project+myproject'}
        self._test_create(create_data, 'SLICE', 'SLICE_URN', 3)

        #Asserting to make sure the unauthorized_field was not created
        lookup_data = {'SLICE_PROJECT_URN': 'urn:publicid:IDN+this_sa+project+myproject'}
        self.assertEqual(self._test_lookup(lookup_data,None,'SLICE',0), {})

    def test_update_unauthorized_field(self):
        """
        Test update rules by passing an unauthorized field ('KEY_TYPE') during creation.
        """
        create_data = {'PROJECT_EXPIRATION':'2014-03-21T11:35:57Z', 'PROJECT_NAME': 'TEST_PROJECT', 'PROJECT_DESCRIPTION':'My test project'}
        urn = self._test_create(create_data, 'PROJECT', 'PROJECT_URN', 0)
        update_data = {'PROJECT_NAME' : 'UNAUTHORIZED_UPDATE'}
        self._test_update(urn, update_data, 'PROJECT', 'PROJECT_URN', 3)
        self._test_delete(urn, 'PROJECT', 'PROJECT_URN', 0)

    def test_update_invalid_expiry(self):
        """
        Test update rules by passing an invalid expiry date during update.
        Note: We are only testing projects here because otherwise we would end up with slices left over (we can not remove slices).
        """
        create_data = {
                       'PROJECT_NAME' : 'TEST-PROJECT',
                       'PROJECT_DESCRIPTION' : 'Time_Expiry'}

        urn = self._test_create(create_data, 'PROJECT', 'PROJECT_URN', 0)

        update_data = {'PROJECT_EXPIRATION' : '2013-07-29T13:15:30Z'}
        self._test_update(urn, update_data, 'PROJECT', 'PROJECT_URN', 3)
        self._test_delete(urn, 'PROJECT', 'PROJECT_URN', 0)

    def test_lookup_multiple_slice_urns(self):
        create_data_1 = {
               'SLICE_NAME' : 'TEST-SLICE-1',
               'SLICE_DESCRIPTION' : 'Time_Expiry'}

        create_data_2 = {
               'SLICE_NAME' : 'TEST-SLICE-2',
               'SLICE_DESCRIPTION' : 'Time_Expiry'}

        urn1 = self._test_create(create_data_1, 'SLICE', 'SLICE_URN', 0)
        urn2 = self._test_create(create_data_2, 'SLICE', 'SLICE_URN', 0)

        lookup_data={'SLICE_URN':[str(urn1),str(urn2)]}
        self._test_lookup(lookup_data, None, 'SLICE', 0, 2)

    def test_slice(self):
        """
        Test object type 'SLICE' methods: create, lookup, update.

        Slice deletion method is explicity blocked by the API specification: 'No
        SA should support slice deletion since there is no authoritative way to
        know that there aren't live slivers associated with that slice.' In this
        case, we check that the method returns an error.

        There is a situation when the test data has been used once, as the key
        will already exist (and cannot be deleted). In this case, we check if
        the slice already exists. If it does, then we expect a duplicate error
        when creating a new 'SLICE'. If it is not already present, we should
        expect regular object creation.

        When checking if the object already exists, we need to remove the same
        field that is later used in the update operation, as it *may* not match
        otherwise. This is because it *could* have been updated in the case that
        the object already exists.

        Similarly, if the object creation fails because the key already exists,
        we need to get the URN from the previous 'lookup' call which should have
        returned a result.
        """
        create_data = {'SLICE_NAME':'AUTHORIZED-CREATION', 'SLICE_DESCRIPTION' : 'My Clean Slice', 'SLICE_PROJECT_URN' : 'urn:publicid:IDN+this_sa+project+myproject'}
        lookup_data = _remove_key(create_data, 'SLICE_DESCRIPTION')
        presence_check = self._test_lookup(lookup_data, None, 'SLICE', 0)
        if len(presence_check) is 1:
            create_code = 5
        else:
            create_code = 0
        urn = self._test_create(create_data, 'SLICE', 'SLICE_URN', create_code)
        update_data = {'SLICE_DESCRIPTION' : 'Update Slice'}
        if urn is None:
            urn, _ = presence_check.popitem()
        self._test_update(urn, update_data, 'SLICE', 'SLICE_URN', 0)
        self._test_delete(urn, 'SLICE', 'SLICE_URN', 100)

    def test_sliver_info(self):
        """
        Test object type 'SLIVER_INFO' methods: create, lookup, update and delete.
        """
        create_data = { 'SLIVER_INFO_SLICE_URN' : 'urn:publicid:IDN+this.sa+slice+TESTSLICE', 'SLIVER_INFO_URN' : 'urn:publicid:IDN+this.sa+slice+TESTSLICE',
            'SLIVER_INFO_AGGREGATE_URN' : 'urn:publicid:IDN+this.sa+slice+TESTSLICE', 'SLIVER_INFO_CREATOR_URN' : 'urn:publicid:IDN+this.sa+slice+TESTSLICE',
            'SLIVER_INFO_EXPIRATION' : '2014-03-21T11:35:57Z', 'SLIVER_INFO_CREATION' : '2014-03-21T11:35:57Z'}
        urn = self._test_create(create_data, 'SLIVER_INFO', 'SLIVER_INFO_URN', 0)
        update_data = {'SLIVER_INFO_EXPIRATION' : '2014-04-21T11:35:57Z'}
        self._test_update(urn, update_data, 'SLIVER_INFO', 'SLIVER_INFO_URN', 0)
        self._test_delete(urn, 'SLIVER_INFO', 'SLIVER_INFO_URN', 0)

    def test_project(self):
        """
        Test object type 'PROJECT' methods: create, lookup, update and delete.
        """
        create_data = {'PROJECT_EXPIRATION':'2014-03-21T11:35:57Z', 'PROJECT_NAME': 'TEST_PROJECT', 'PROJECT_DESCRIPTION':'My test project'}
        urn = self._test_create(create_data, 'PROJECT', 'PROJECT_URN', 0)
        update_data = {'PROJECT_DESCRIPTION' : 'M. Broadbent Test Project'}
        self._test_update(urn, update_data, 'PROJECT', 'PROJECT_URN', 0)
        self._test_delete(urn, 'PROJECT', 'PROJECT_URN', 0)

    def _test_create(self, fields, object_type, expected_urn, expected_code):
        """
        Helper method to test object creation.
        """
        code, value, output = sa_call('create', [object_type, self._credential_list("admin"), {'fields' : fields}], user_name="admin")

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
        code, value, output = sa_call('update', [object_type, urn, self._credential_list("admin"), {'fields' : fields}], user_name="admin")
        self.assertEqual(code, expected_code)
        if code is 0:
            self.assertIsNone(value)
            result = self._test_lookup({expected_urn : urn}, None, object_type, 0, 1)
            for field_key, field_value in fields.iteritems():
                self.assertEqual(result[urn].get(field_key), field_value)

    def _test_lookup(self, match, _filter, object_type, expected_code, expected_length=None):
        """
        Helper method to test object lookup.
        """
        options = {}
        if match:
            options['match'] = match
        if _filter:
            options['filter'] = _filter
        code, value, output = sa_call('lookup', [object_type, self._credential_list("admin"), options], user_name="admin")
        self.assertEqual(code, expected_code)
        if expected_length:
            self.assertEqual(len(value), expected_length)
        return value

    def _test_delete(self, urn, object_type, expected_urn, expected_code):
        """
        Helper method to test object deletion.
        """
        code, value, output = sa_call('delete', [object_type, urn, self._credential_list("admin"), {}], user_name="admin")
        self.assertEqual(code, expected_code)
        self.assertIsNone(value)
        self._test_lookup({expected_urn : urn}, None, object_type, 0)

    def test_malformed_membership(self):
        """
        Test type checking by passing incorrect (project) parameters in a slice
        membership call.
        """
        add_data = {'members_to_add' : [{'PROJECT_MEMBER' : 'test_urn', 'PROJECT_ROLE' : 'test_role'}]}
        self._test_lookup_members('urn:publicid:IDN+this.sa+project+SLICE', 'SLICE', add_data, 0, 3)

    def test_project_membership(self):
        """
        Test the 'add', 'change' and 'remove' methods for 'PROJECT' membership
        object.
        """
        add_data = {'members_to_add' : [{'PROJECT_MEMBER' : 'test_urn', 'PROJECT_ROLE' : 'test_role'}]}
        change_data = {'members_to_change' : [{'PROJECT_MEMBER' : 'test_urn', 'PROJECT_ROLE' : 'upgraded_test_role'}]}
        remove_data = {'members_to_remove' : [{'PROJECT_MEMBER' : 'test_urn'}]}
        self._test_lookup_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'PROJECT', add_data, 1, 0)
        self._test_lookup_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'PROJECT', change_data, 1, 0)
        self._test_lookup_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'PROJECT', remove_data, 0, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'test_urn','PROJECT', add_data, 1, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'test_urn','PROJECT', change_data, 1, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+project+TESTPROJECT', 'test_urn', 'PROJECT', remove_data, 0, 0)

    def test_slice_membership(self):
        """
        Test the 'add', 'change' and 'remove' methods for 'PROJECT' membership
        object.
        """
        add_data = {'members_to_add' : [{'SLICE_MEMBER' : 'test_urn', 'SLICE_ROLE' : 'test_role'}]}
        change_data = {'members_to_change' : [{'SLICE_MEMBER' : 'test_urn', 'SLICE_ROLE' : 'upgraded_test_role'}]}
        remove_data = {'members_to_remove' : [{'SLICE_MEMBER' : 'test_urn'}]}
        self._test_lookup_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'SLICE', add_data, 1, 0)
        self._test_lookup_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'SLICE', change_data, 1, 0)
        self._test_lookup_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'SLICE', remove_data, 0, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'test_urn','SLICE', add_data, 1, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'test_urn','SLICE', change_data, 1, 0)
        self._test_lookup_for_members('urn:publicid:IDN+this.sa+slice+TESTSLICE', 'test_urn', 'SLICE', remove_data, 0, 0)

    def _test_modify_membership(self, urn, object_type, data, expected_code):
        """
        Helper method to test object membership modification.
        """
        code, value, output = sa_call('modify_membership', [object_type, urn, self._credential_list("admin"), data], user_name="admin")
        self.assertEqual(code, expected_code)
        return code

    def _test_lookup_members(self, urn, object_type, data, expected_length, expected_code):
        """
        Helper method to test object membership lookup.
        """
        if self._test_modify_membership(urn, object_type, data, expected_code) is 0:
            code, value, output = sa_call('lookup_members', [object_type, urn, self._credential_list("admin"), {}], user_name="admin")
            self.assertEqual(code, 0)
            self.assertEqual(len(value), expected_length)

    def _test_lookup_for_members(self, urn, member_urn, object_type, data, expected_length, expected_code):
        """
        Helper method to test object membership lookup for a member.
        """
        if self._test_modify_membership(urn, object_type, data, expected_code) is 0:
            code, value, output = sa_call('lookup_for_member', [object_type, member_urn, self._credential_list("admin"), {}], user_name="admin")
            self.assertEqual(code, 0)
            self.assertEqual(len(value), expected_length)

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
    if len(sys.argv) == 2:
        arg = sys.argv[1]
    del sys.argv[1:]
    unittest.main(verbosity=0, exit=True)
    print_warnings()
