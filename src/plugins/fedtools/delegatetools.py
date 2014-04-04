from amsoil.core import serviceinterface
from amsoil.config import expand_amsoil_path
import amsoil.core.pluginmanager as pm
import amsoil.core.log

from delegateexceptions import *
from apiexceptions import *

import os.path
import json
import uuid
import pyrfc3339
import re

logger = amsoil.core.log.getLogger('delegatetools')

class DelegateTools(object):
    """
    Common tools used to implement a ClearingHouse (CH) delegate.
    """

    JSON_COMMENT = "__comment" #: delimeter for comments in loaded JSON files (config.json and defaults.json)
    STATIC = {} #: holds static configuration and settings loaded from JSON files (config.json and defaults.json)
    REQUIRED_METHOD_KEYS = ['members_to_add', 'members_to_change', 'members_to_remove'] #: list of valid keys to be passed as 'options' in a 'modify_membership' call
    GET_VERSION_FIELDS = ['URN', 'IMPLEMENTATION', 'SERVICES', 'CREDENTIAL_TYPES', 'ROLES', 'SERVICE_TYPES', 'API_VERSIONS'] #: list of fields possible in a 'get_version' API call response

    def __init__(self):
        """
        Load configuration files. Combine the default field names with the supplemenary fields to form a combined list.
        """
        self._load_files()
        self._combine_fields()

    def _load_files(self):
        """
        Load JSON configuration and default files.

        Raises:
            MalformedConfigFile: An error occured when loading the JSON file.

        """
        paths = self._get_paths()
        for path_key, path_value in paths.iteritems():
            if not os.path.exists(path_value):
                raise ConfigFileMissing(path_value)
            try:
                self.STATIC[path_key] = self._strip_comments(json.load(open(path_value)))
            except Exception:
                raise MalformedConfigFile(path_value, '')

    def _combine_fields(self):
        """
        Combine default fields with supplementary fields to form a combined set.

        Supplementary fields can also overwrite exsiting default fields.

        """
        self.STATIC['COMBINED'] = self.STATIC['DEFAULTS']
        for type_key, type_value in self.STATIC['CONFIG'].iteritems():
            if type_key not in self.JSON_COMMENT:
                for field_key, field_value in type_value.get('SUPPLEMENTARY_FIELDS').iteritems():
                    self.STATIC['COMBINED'][type_key.upper()][field_key.upper()] = field_value

    def _strip_comments(self, json):
        """
        Recursively strip comments out of loaded JSON files.

        The delimeter used to define a comment is defined in a global variable (JSON_COMMENT).

        Args:
            json: JSON content to strip comments from

        Returns:
            JSON content with comments removed

        """
        if type(json) in [str, unicode, int, float, bool, type(None)]:
            return json
        if isinstance(json, list):
            return [self._strip_comments(j) for j in json if not ((type(j) in [str, unicode]) and j.startswith(self.JSON_COMMENT))]
        if isinstance(json, dict):
            return dict( (k, self._strip_comments(v)) for (k,v) in json.iteritems() if k != self.JSON_COMMENT) # there would be a dict comprehension from 2.7

    def _get_paths(self):
        """
        Get full file paths for JSON files to load (config.json and defaults.json).

        Returns:
            dictionary containing the loaded JSON content

        """
        config = pm.getService("config")
        config_path = config.get("delegatetools.config_path")
        defaults_path = config.get("delegatetools.defaults_path")
        return {'CONFIG' : expand_amsoil_path(config_path), 'DEFAULTS' : expand_amsoil_path(defaults_path)}

    @serviceinterface
    def get_fields(self, type_):
        """
        Get combined fields for a given object type.

        Args:
            type_: the type of object

        Returns:
            the combined fields

        """
        return self.STATIC['COMBINED'][_type]

    @serviceinterface
    def get_supplementary_fields(self, types):
        """
        Get supplementary fields for a set of given object types.

        Args:
            types: a list of object types

        Returns:
            the supplementary fields

        """
        result = {}
        for _type in types:
            try:
                result.update(self.STATIC['CONFIG'][_type].get('SUPPLEMENTARY_FIELDS', None))
            except KeyError:
                pass
        return result

    @serviceinterface
    def get_config(self, type_):
        """
        Get configuration fields for a given object type.

        Args:
            type_: the type of object

        Returns:
            the configuration fields

        """
        return self.STATIC['CONFIG'].get(type_, {})

    @serviceinterface
    def get_version(self, resource_manager):
        """
        Get details for a 'get_version' response by calling relevant methods in the corresponding resource manager.

        If the method is not available, it implies that this field is not required/supported.

        Args:
            resource_manager: Resource Manager instance to request information from

        Returns:
            complete 'get_version' response

        """

        version = {}
        for field in self.GET_VERSION_FIELDS:
            if hasattr(resource_manager, field.lower()):
                version[field] = getattr(resource_manager, field.lower())()
        return version

    @serviceinterface
    def get_whitelist(self, type_):
        """
        Forms a number of whitelists for a given object type.

        Lists formed include:
            * create_whitelist: fields that can be passed in 'create' operation
            * create_required: fields that must be passed in a 'create' operation
            * update_whitelist: fields that can be passed in an 'update' operation
            * lookup_match: fields that can be passed in a 'lookup' operation's 'match' field
            * lookup_protected: fields that must be protected in a 'lookup' operation
            * lookup_identifying: fields that identify a user in a 'lookup' operation

        Protected and identify information is to be given out according to
        implementation-specific privileges of requesting user

        Args:
            type_: the type of object

        Returns:
            dictionary of whitelists
        """
        combined_fields = self.STATIC['COMBINED'][type_]
        whitelist = {'create_whitelist' : [], 'create_required' : [],
            'update_whitelist' : [], 'lookup_match' : [], 'lookup_private' : [],
            'lookup_identifying' : []}
        for field_key, field_value in combined_fields.iteritems():
            whitelist = self._get_fields_values(whitelist, field_key, field_value)
        return whitelist

    def _get_fields_values(self, whitelist, field_key, field_value):
        """
        Set whitelist values for a given field.

        Fields and defaults as per: http://groups.geni.net/geni/wiki/CommonFederationAPIv2#APIget_versionmethods

        Args:
            whitelist: dictionary of whitelists to update
            field_key: key for field
            field_value: value for field

        Returns:
            dictionary of whitelists

        """
        if field_value.get('CREATE', 'NOT ALLOWED') in ['REQUIRED', 'ALLOWED']:
            whitelist['create_whitelist'].append(field_key)
            if field_value.get('CREATE', False) is 'REQUIRED':
                whitelist['create_required'].append(field_key)
        if field_value.get('MATCH', True):
            whitelist['lookup_match'].append(field_key)
        if field_value.get('UPDATE', False):
            whitelist['update_whitelist'].append(field_key)
        protect = field_value.get('PROTECT', 'PUBLIC')
        if protect is 'IDENTIFYING':
            whitelist['lookup_identifying'].append(field_key)
        if protect is 'PRIVATE':
            whitelist['lookup_private'].append(field_key)
        return whitelist

    @serviceinterface
    def member_check(self, required_field_keys, options):
        """
        Check correctly formed options for 'modify_membership' method.

        Ensures method is one of 'members_to_add', 'members_to_change' or 'members_to_remove'.

        Args:
            required_field_keys: keys to add, change or remove are dependent on object type (Slice Member or Project Member)
            options: call parameters to check

        Raises:
            GFedv2ArgumentError: There is an inconsitency in the options given

        """
        for method_key, method_value in options.iteritems():
            if method_key in self.REQUIRED_METHOD_KEYS:
                for item in  method_value:
                    for field_key in item.iterkeys():
                        if not field_key in required_field_keys:
                            raise GFedv2ArgumentError("Member key to modify not of required type. Offending key is: " + str(field_key) + ". Should be one of these types: " + str(required_field_keys))
            else:
                raise GFedv2ArgumentError("Member method key not found. Offending key is: " + str(method_key) + ". Should be one of these types: " + str(self.REQUIRED_METHOD_KEYS))

    @serviceinterface
    def slice_name_check(self, slice_name):
        if not re.match(r'^[a-zA-Z0-9][ A-Za-z0-9_-]{1,19}$', slice_name):
            raise GFedv2ArgumentError('SLICE_NAME field must be <= 19 characters, must only contain alphanumeric characters or hyphens and those hyphens must not be leading.')

    @serviceinterface
    def object_creation_check(self, fields, whitelist):
        """
        Check if the given fields can be used in creating an object.

        Args:
            fields: fields to verify
            whitelist: field names to check against

        Raises:
            GFedv2ArgumentError: There is a required field missing or it is not possible to pass this field during object creation.

        """
        required = set(whitelist.get('create_required')).difference(set(fields))
        whitelist = set(fields).difference(set(whitelist.get('create_whitelist')))
        if required:
            raise GFedv2ArgumentError('Required key(s) missing for object creation: ' + ', '.join(required))
        if whitelist:
            raise GFedv2ArgumentError('Cannot pass the following key(s) when creating an object : ' + ', '.join(whitelist))

    @serviceinterface
    def object_update_check(self, fields, whitelist):
        """
        Check if the given fields can be used in updating an object.

        Args:
            fields: field names to verify
            whitelist: field names to check against

        Raises:
            GFedv2ArgumentError: It is not possible to pass this field during an object update.

        """
        whitelist = set(fields).difference(set(whitelist.get('update_whitelist')))
        if whitelist:
            raise GFedv2ArgumentError('Cannot pass the following key(s) when updating an object : ' + ', '.join(whitelist))

    @serviceinterface
    def object_consistency_check(self, type_, fields):
        """
        Check that fields conform to a predefined type by calling a corresponding method.

        Args:
            type_: the type of object
            fields: fields to verify

        Raises:
            GFedv2ArgumentError: Inconsistency found between a field value and the required type.

        """
        combined = self.STATIC['COMBINED'][type_]
        for key, value in fields.iteritems():
            if self.JSON_COMMENT not in key and value is not None:
                field_type = combined[key.upper()].get('TYPE')
                try:
                    getattr(TypeCheck, 'check_' + field_type.lower())(value)
                except AttributeError:
                    raise GFedv2ArgumentError('No type check available for: ' + field_type + '. Please check your supplementary fields for valid data types. ' +
                        'See http://groups.geni.net/geni/wiki/CommonFederationAPIv2#AppendixB:APIDataTypes for more details.')
                except Exception:
                    raise GFedv2ArgumentError('Field {' + key + ' : ' + str(value) + '} is not of type ' + field_type)


    @serviceinterface
    def to_keyed_dict(self, list_, key):
        """
        Convert a list to a dictionary, keyed to given key.

        Args:
            list_: list object use for conversion
            key: field to use as dictionary key

        Returns:
            keyed dictionary

        """
        for d in list_:
            if not key in d:
                raise ValueError("Can not convert to dict because the key_field name (%s) is not in the dictionary (%s)" % (key, d))
        return { d[key] : dict(filter(lambda (k,v): (k != key), d.iteritems())) for d in list_}

    @serviceinterface
    def match_and_filter(self, list_of_dicts, field_filter, field_match):
        """
        Takes a list of dicts and applies the given filter and matches the results (please GENI Federation API on how matching and filtering works).
        if field_filter is None the unfiltered list is returned.
        """
        return [self._filter_fields(d, field_filter) for d in list_of_dicts if self._does_match_fields(d, field_match)]

    def _does_match_fields(self, d, field_match):
        """
        Returns if the given dictionary matches the {field_match}.
        {field_match} may look like: { 'must_be' : 'this', 'and_any_of_' : ['tho', 'se']}
        """
        if not field_match:
            return True
        for mk, mv in field_match.iteritems(): # each matches must be fulfilled
            val = d[mk]
            if isinstance(mv, list): # any of those values (OR)
                found_any = False;
                for mvv in mv:
                    if val == mvv:
                        found_any = True
                if not found_any:
                    return False
            else: # or explicitly this one
                if not val == mv:
                    return False
        return True

    def _filter_fields(self, d, field_filter):
        """Takes a dictionary and applies the filter. Returns the unfiltered d if None is given."""
        if not field_filter:
            return d
        result = {}
        for f in field_filter:
            result[f] = d[f]
        return result

class TypeCheck():
    """
    Used as a holder for various type checks used in 'object_consistency_check' method.
    """

    @staticmethod
    def check_urn(value):
        """
        Check if value is a valid URN string

        See wiki for more details: http://groups.geni.net/geni/wiki/GeniApiIdentifiers

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid URN string

        """
        if not re.match(r"^urn:publicid:IDN+\+[A-Za-z0-9\._:-]+\+[A-Za-z0-9]+\+[A-Za-z0-9\._+:-]*$", value):
            raise Exception

    @staticmethod
    def check_url(value):
        """
        Check if value is a valid URL string

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid URL string

        """
        regex = re.compile(
            r'^(?:http)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not re.match(regex, value):
            raise Exception

    @staticmethod
    def check_uid(value):
        """
        Check if value is a valid UUID string.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid UID string

        """
        uuid.UUID(value)

    @staticmethod
    def check_string(value):
        """
        Check if value is a valid String.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type String

        """
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_integer(value):
        """
        Check if value is a valid Integer.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type Integer

        """
        if not isinstance(value, int):
             raise Exception

    @staticmethod
    def check_datetime(value):
        """
        Check if value is a valid RFC3339 string.

        See RFC3339 for more details: http://www.ietf.org/rfc/rfc3339.txt

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid RFC3339 string

        """
        pyrfc3339.parse(value)

    @staticmethod
    def check_email(value):
        """
        Check if value is a valid email string.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid email string

        """
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", value):
            raise Exception

    @staticmethod
    def check_key(value):
        """
        Check if value is a valid key string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid key string

        """
        # TODO: check key validity - SSH or SSL public or private key
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_boolean(value):
        """
        Check if value is a valid Boolean.

        Args:
            value: item to check

        Raises:
            Exception: value is not of type Boolean

        """
        if not isinstance(value, bool):
            raise Exception

    @staticmethod
    def check_credentials(value):
        """
        Check if value is a valid credential string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid credential string

        """
        # TODO: check credential validity with geni_trust
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_certificate(value):
        """
        Check if value is a valid certificate string.

        Should be contents, rather than filename.
        Incomplete implementation. Only very basic object check currently.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid certificate string

        """
        # TODO: check certificate validity with geni_trust
        if not isinstance(value, basestring):
            raise Exception

    @staticmethod
    def check_list_of_dictionaries(value):
        """
        Check if value is a valid list of dictionaries.

        Args:
            value: item to check

        Raises:
            Exception: value is not of valid  list of dictionaries

        """
        if not isinstance(value, list):
            raise Exception
        for dictionary in value:
            if not isinstance(dictionary, dict):
                raise Exception
