from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm
import amsoil.core.log
from apiexceptions import *

logger=amsoil.core.log.getLogger('resourcemanagertools')

class ResourceManagerTools(object):
    """
    Common tools used to implement a ClearingHouse (CH) Resource Manager (RM).
    """

    def __init__(self):
        """
        Load database (MongoDB) plugin.
        """
        self._database = pm.getService('mongodb')

    @serviceinterface
    def set_index(self, collection, index):
        """
        Set a unique key for a given collection.

        Args:
            collection: collection to set unique key in
            key: unique key to set

        """
        self._database.set_index(collection, index)

    @serviceinterface
    def member_modify(self, authority, type_, urn, options, member_key, urn_key):
        """
        Modify a membership in the database.

        Can be 'add', 'remove' or 'update'; corresponding method called accordingly.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            type_: type of object to use in action ('slice_member' or 'project_member')
            urn: URN of slice or project to use in action
            options: 'options' dictionary passed in original API call
                (contains 'members_to_add', 'members_to_remove' and/or 'members_to_change' lists)
            member_key: name of member key to use in update action ('SLICE_MEMBER' or 'PROJECT_MEMBER')
            urn_key: name of URN key to use in action ('SLICE_URN' or 'PROJECT_URN')

        Returns:
            none

        """
        for option_key, option_value in options.iteritems():
            getattr(self, '_' + option_key)(authority, type_, urn, option_value, member_key, urn_key)
        return None

    def _members_to_add(self, authority, type_, urn, option_value, _, urn_key):
        """
        Add a new member relationship to the database.

        Args:
            authority:
            type_:
            urn:
            option_value:
            urn_key:
        """
        for members_dict in option_value:
            members_dict['type'] = type_
            members_dict[urn_key] = urn
            self._database.create(authority, members_dict)

    def _members_to_remove(self, authority, type_, urn, option_value, _, urn_key):
        """
        Remove members from database.
        """
        for members_dict in option_value:
            members_dict['type'] = type_
            members_dict[urn_key] = urn
            self._database.delete(authority, members_dict)

    def _members_to_change(self, authority, type_, urn, option_value, member_key, urn_key):
        """
        Update members in database.
        """
        for members_dict in option_value:
            members_dict['type'] = type_
            members_dict[urn_key] = urn
            update_fields = {member_key : members_dict.get(member_key), 'type' :  type_}
            self._database.update(authority, update_fields, members_dict)

    @serviceinterface
    def member_lookup(self, authority, type_, key, value, extra_fields=None):
        """
        Lookup membership (SLICE_MEMBERSHIP, PROJECT_MEMBERSHIP) in the database.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            type_: type of object to delete ('member', 'slice', etc.)
            match: search fields in database
            filter_: fields to be present in returned result

        Returns:
            a number of results from the database, pruned of implementation-specific fields

        """
        if extra_fields is None:
            extra_fields = []
        result = self._database.lookup(authority, {'type': type_, key : value}, {})
        for member in result:
            member = self._database.prune_result(member, extra_fields)
        return result

    @serviceinterface
    def object_create(self, authority, fields, type_):
        """
        Create object (SLICE, MEMBER, etc.) in the database.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            fields: fields of values to update
            type_: type of object to delete ('member', 'slice', etc.)

        Returns:
            dictionary of with fields of new object

        """
        create_fields = {}
        for key, value in fields.iteritems():
            create_fields[key] = value
        create_fields['type'] = type_
        try:
            self._database.create(authority, create_fields)
        except Exception as e:
            raise GFedv2DuplicateError(str(e))
        result = self._database.prune_result(create_fields)
        return result

    @serviceinterface
    def object_update(self, authority, fields, type_, urn):
        """
        Update object (SLICE, MEMBER, etc.) in the database.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            fields: fields of values to update
            type_: type of object to delete ('member', 'slice', etc.)
            urn: unique identifier of object to update

        Returns:
            none

        """
        update_fields = {}
        for key, value in fields.iteritems():
            update_fields[key] = value
        urn['type'] = type_
        self._database.update(authority, urn, update_fields)
        return None

    @serviceinterface
    def object_lookup(self, authority, type_, match, filter_):
        """
        Lookup object (SLICE, MEMBER, etc.) in the database.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            type_: type of object to delete ('member', 'slice', etc.)
            match: search fields in database
            filter_: fields to be present in returned result

        Returns:
            a number of results from the database, pruned of implementation-specific fields

        """
        # TODO: Convert the prune to whitelist rather than
        match['type'] = type_
        filter_ = self._convert_filter_to_projection(filter_)
        results = self._database.lookup(authority, match, filter_)
        for result in results:
            result = self._database.prune_result(result)

        return results

    def _convert_filter_to_projection(self, filter_):
        """
        Convert 'filter' field to 'projection' format.

        See MongoDB documentation for more details: http://docs.mongodb.org/manual/reference/method/db.collection.find/

        Args:
            filter_: 'filter' field from call 'options'

        Returns:
            dictionary of fields that should be present in the 'lookup' result

        """
        projection = {'_id' : False}
        for field in filter_:
            projection[field] = True
        return projection

    @serviceinterface
    def object_delete(self, authority, type_, urn):
        """
        Remove object (SLICE, MEMBER, etc.) from the database.

        Args:
            authority: authority ('sa' or 'ma') to which the object belongs
            type_: type of object to delete ('member', 'slice', etc.)
            urn: unique identifier of object to delete

        Returns:
            none

        """
        urn['type'] = type_
        self._database.delete(authority, urn)
        return None

    @serviceinterface
    def form_api_versions(self, hostname, port, endpoints):
        """
        Form 'api_versions' field for 'get_version' method call.

        Args:
            hostname: authority hostname
            port: authority port number
            endpoints: dictionary of endpoints (urls and version numbers)

        Returns:
            'api_versions' dictionary for insertion into 'get_version' response

        """
        api_versions = {}
        for endpoint in endpoints:
            api_versions[endpoint.get('version')] = 'https://' + hostname + ':' + port + endpoint.get('url')
        return api_versions
