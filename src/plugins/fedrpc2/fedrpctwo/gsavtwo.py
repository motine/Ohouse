import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gsarpc')

import gapitools

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GSAv2Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GSAv2Handler, self).__init__(logger)
        self._delegate = None
    
    # ---- General Methods
    @serviceinterface
    def setDelegate(self, adelegate):
        self._delegate = adelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

    def get_version(self):
        pass

    def create(self, _type, credentials, options):
        pass

    def update(self, _type, urn, credentials, options):
        pass

    def delete(self, _type, urn, credentials, options):
        pass

    def lookup (self, _type, credentials, options):
        pass

    # ---- Slice Service Methods
    def get_credentials(self, slice_urn, credentials, options):
        pass

    # ---- Slice Member Service Methods and Project Member Service Methods
    def modify_membership(self, _type, urn, credentials, options):
        pass
    
    def lookup_members(self, _type, urn, credentials, options):
        pass

    def lookup_for_member(self, _type, member_urn, credentials, options):
        pass

class GSAv2DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v2).
    {match}, {filter} and {fields} semantics are explained in the GENI Federation API document.
    """
    
    def __init__(self):
        super(GSAv2DelegateBase, self).__init__()
    
    # ---- General methods
    def get_version(self):
        """
        Return information about version and options 
          (e.g. filter, query, credential types) accepted by this service

        Arguments: None

        Return:
            get_version structure information as described above
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def create(self, _type, credentials, options):
        """
        Creates a new instance of the given object with a 'fields' option 
        specifying particular field values that are to be associated with the object. 
        These may only include those fields specified as 'ALLOWED or 'REQUIRED' 
        in the 'Creation' column of the object descriptions below 
        or in the 'CREATE' key in the supplemental fields in the 
        get_version specification for that object. 
        If successful, the call returns a dictionary of the fields 
        associated with the newly created object.


        Arguments:

           type : type of object to be created
          options: 
              'fields', a dictionary field/value pairs for object to be created

        Return:
          Dictionary of object-type specific field/value pairs for created object 
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def update(self, _type, urn, credentials, options):
        """
        Updates an object instance specified by URN with a 'fields' option 
         specifying the particular fields to update. 
        Only a single object can be updated from a single update call. 
        The fields may include those specified as 'Yes' in the 'Update' column 
        of the object descriptions below, or 'TRUE' in the 'UPDATE' key in the 
        supplemental fields provided by the get_version call. 
        Note: There may be more than one entity of a given URN at an authority, 
        but only one 'live' one (any other is archived and cannot be updated).
        
        Arguments:
          type: type of object to be updated
          urn: URN of object to update
            (Note: this may be a non-URN-formatted unique identifier e.g. in the case of keys)
          options: Contains 'fields' key referring dictionary of 
               name/value pairs to update
        
        Return: None
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def delete(self, _type, urn, credentials, options):
        """
        Deletes an object instance specified by URN 
        Only a single object can be deleted from a single delete call. 
        Note: not all objects can be deleted. In general, it is a matter
            of authority policy.

        Arguments:
          type: type of object to be deleted
          urn: URN of object to delete
            (Note: this may be a non-URN-formatted unique identifier e.g. in the case of keys)

        Return: None
        """
        raise GFedv2NotImplementedError("Method not implemented")

    def lookup(self, _type, credentials, options):
        """
        Lookup requested details for objects matching 'match' options. 
        This call takes a set of 'match' criteria provided in the 'options' field, 
        and returns a dictionary of dictionaries of object attributes 
        keyed by object URN matching these criteria. 
        If a 'filter' option is provided, only those attributes listed in the 'filter' 
        options are returned. 
        The requirements on match criteria supported by a given service 
        are service-specific; however it is recommended that policies 
        restrict lookup calls to requests that are bounded 
        to particular sets of explicitly listed objects (and not open-ended queries).

        See additional details on the lookup method in the document section below.


        Arguments:
           type: type of objects for which details are being requested
           options: What details to provide (filter options) 
                   for which objects (match options)

        Return: List of dictionaries (indexed by object URN) with field/value pairs 
          for each returned object
        """
        raise GFedv2NotImplementedError("Method not implemented")

    # ---- Slice Service Methods
    SLICE_DEFAULT_FIELDS = {
        "SLICE_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of given slice",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLICE_UID" : {
            "TYPE"    : "UID",
            "DESC"    : "UID (unique within authority) of slice",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLICE_CREATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Creation time of slice",
            "MATCH"   : False},
        "SLICE_EXPIRATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Expiration time of slice",
            "MATCH"   : False,
            "UPDATE"  : True },
        "SLICE_EXPIRED" : {
            "TYPE"    : "BOOLEAN",
            "DESC"    : "Whether slice has expired",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLICE_NAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Short name of Slice",
            "MATCH"   : False,
            "UPDATE"  : False },
        "SLICE_DESCRIPTION" : {
            "TYPE"    : "STRING",
            "DESC"    : "Description of Slice",
            "MATCH"   : False,
            "UPDATE"  : True },
        "SLICE_PROJECT_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of project to which slice is associated (if SA supports project)",
            "MATCH"   : True,
            "UPDATE"  : False }}

    def get_credentials(slice_urn, credentials, options):
        """
        Provide list of credentials for the caller relative to the given slice. 
        If the invocation is in a speaks-for context, the credentials will be for the 
        'spoken-for' member, not the invoking tool.

        For example, this call may return a standard SFA Slice Credential and some 
        ABAC credentials indicating the role of the member with respect to the slice.

        Note: When creating an SFA-style Slice Credential, the following roles 
        typically allow users to operate at known GENI-compatible 
        aggregates: "*" (asterisk)  or the list of "refresh", "embed", 
           "bind", "control" "info".

        Arguments:
          slice_urn: URN of slice for which to get member's credentials
          options: Potentially contains 'speaking_for' key indicating a speaks-for 
             invocation (with certificate of the accountable member 
             in the credentials argument)

        Return:
          List of credential in 'CREDENTIALS' format, i.e. a list of credentials with 
        type information suitable for passing to aggregates speaking AM API V3.
        """
        raise GFedv1NotImplementedError("Method not implemented")

     # ---- Slice Member Service Methods and Project Member Service Methods

    def modify_membership(self, _type, urn, credentials, options):
        """
        Modify object membership, adding, removing and changing roles of members 
           with respect to given object

        Arguments:
          type: type of object for whom to lookup membership (
              in the case of Slice Member Service, "SLICE", 
              in the case of Project Member Service, "PROJECT")
          urn: URN of slice/project for which to modify membership
          Options:
              members_to_add: List of member_urn/role tuples for members to add to 
                     slice/project of form 
                        {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role} 
                           (or 'PROJECT_MEMBER/PROJECT_ROLE 
                           for Project Member Service)
              members_to_remove: List of member_urn of members to 
                       remove from slice/project
              members_to_change: List of member_urn/role tuples for 
                        members whose role 
                       should change as specified for given slice/project of form 
                       {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role} 
                       (or 'PROJECT_MEMBER/PROJECT_ROLE for Project Member Service)

        Return:
          None
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_members(self, _type, urn, credentials, options):
        """
        Lookup members of given object and their roles within that object
        
        Arguments:
          type: type of object for whom to lookup membership 
                 (in the case of Slice Member Service, "SLICE", 
                  in the case of Project Member Service, "PROJECT")
          urn: URN of object for which to provide current members and roles
        
        Return:
           List of dictionaries of member_urn/role pairs 
              [{'SLICE_MEMBER': member_urn, 
               'SLICE_ROLE': role }...] 
                (or PROJECT_MEMBER/PROJECT_ROLE 
                 for Project Member Service) 
                 where 'role' is a string of the role name. 
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_for_member(self, _type, member_urn, credentials, options):
        """
        Lookup objects of given type for which the given member belongs

        Arguments:
          Member_urn: The member for whom to find slices to which it belongs

        Return:
           List of dictionary of urn/role pairs 
               [('SLICE_URN' : slice_urn, 'SLICE_ROLE' : role} ...] 
               (or PROJECT_MEMBER/PROJECT_ROLE 
                  for Project Member Service) 
               for each object to which a member belongs, 
               where role is a string of the role name
        """
        raise GFedv1NotImplementedError("Method not implemented")

    # ---- Sliver Info Methods
    SLIVER_INFO_DEFAULT_FIELDS = {
        "SLIVER_INFO_SLICE_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of slice for registered sliver",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLIVER_INFO_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of registered sliver",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLIVER_INFO_AGGREGATE_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of aggregate of registered sliver",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLIVER_CREATOR_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of member/tool that created the registered sliver  ",
            "MATCH"   : True,
            "UPDATE"  : False },
        "SLIVER_INFO_EXPIRATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Time of sliver expiration",
            "MATCH"   : False,
            "UPDATE"  : True },
        "SLIVER_INFO_CREATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Time of sliver expiration",
            "MATCH"   : False,
            "UPDATE"  : False }}

    # ---- Project Service Methods
    PROJECT_DEFAULT_FIELDS = {
        "PROJECT_URN" : {
            "TYPE"    : "URN",
            "DESC"    : "URN of given project",
            "MATCH"   : True,
            "UPDATE"  : False },
        "PROJECT_UID" : {
            "TYPE"    : "UID",
            "DESC"    : "UID (unique within authority) of project",
            "MATCH"   : True,
            "UPDATE"  : False },
        "PROJECT_CREATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Creation time of project",
            "MATCH"   : False,
            "UPDATE"  : False },
        "PROJECT_EXPIRATION" : {
            "TYPE"    : "DATETIME",
            "DESC"    : "Expiration time of project",
            "MATCH"   : False,
            "UPDATE"  : True },
        "PROJECT_EXPIRED" : {
            "TYPE"    : "BOOLEAN",
            "DESC"    : "Whether project has expired",
            "MATCH"   : True,
            "UPDATE"  : False },
        "PROJECT_NAME" : {
            "TYPE"    : "STRING",
            "DESC"    : "Short name of Project",
            "MATCH"   : False,
            "UPDATE"  : False },
        "PROJECT_DESCRIPTION" : {
            "TYPE"    : "STRING",
            "DESC"    : "Description of Project",
            "MATCH"   : False,
            "UPDATE"  : True }}

    # ---- helper methods
    def _match_and_filter_and_to_dict(self, list_of_dicts, key_field, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter_and_to_dict(list_of_dicts, key_field, field_filter, field_match)
    
    def _match_and_filter(self, list_of_dicts, field_filter, field_match):
        """see documentation in gapitools"""
        return gapitools.match_and_filter(list_of_dicts, field_filter, field_match)
    
    def _filter_fields(self, d, field_filter):
        """see documentation in gapitools"""
        return gapitools.filter_fields(d, field_filter)

    def _does_match_fields(self, d, field_match):
        """see documentation in gapitools"""
        return gapitools.does_match_fields(d, field_match)
