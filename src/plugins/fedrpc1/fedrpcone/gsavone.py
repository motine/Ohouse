import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface

import amsoil.core.log
logger=amsoil.core.log.getLogger('gsarpc')

import gapitools

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GSAv1Handler(xmlrpc.Dispatcher):
    def __init__(self):
        super(GSAv1Handler, self).__init__(logger)
        self._delegate = None
    
    # ---- General methods
    @serviceinterface
    def setDelegate(self, adelegate):
        self._delegate = adelegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate

class GSAv1DelegateBase(object):
    """
    The contract of this class (methods, params and returns) are derived from the GENI Federation MA API (v1).
    {match}, {filter} and {fields} semantics are explained in the GENI Federation API document.
    """
    
    def __init__(self):
        super(GSAv1DelegateBase, self).__init__()
    

    def get_version():
        """
        Provide details on the version, services and options supported by this SA

        Arguments:
           Options:

        Return:
          get_version structure information as described above"""
        raise GFedv1NotImplementedError("Method not implemented")

    def create_slice (credentials, options):
        """
        Create a new slice, optionally within a project. See generic create_* method description above.

        Arguments:

          Options: 
              'fields', a dictionary field/value pairs for object to be created

        Return:
          Dictionary of field/value pairs for created slice (e.g. slice URN, slice UUID, expiration and slice credential)

        Should return DUPLICATE_ERROR if creating a slice for which a non-expired slice of same name exists."""
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_slices (credentials, options):
        """
        Lookup slice detail for slices matching 'match' options.

        'filter' options indicate what detail to provide. See generic lookup_* method description above.

        Arguments:
           options: What details to provide (filter options) for which slices (match options)

        Return: List of dictionaries with field/value pairs for each returned slice
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def update_slice(slice_urn, credentials, options):
        """
        Update fields in given slice object. See generic update_* method description above.

        Arguments:
          slice_urn: URN of slice to update

           Options: Contains 'fields' key referring dictionary of name/value pairs to update
        Return: None
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def get_credentials(slice_urn, credentials, options):
        """
        Provide list of credentials for the invoking member relative to the given slice. If the invocation is in a speaks-for context, the credentials will be for the 'spoken-for' member, not the invoking tool.

        For example, this call may return a standard SFA Slice Credential and some ABAC credentials indicating the role of the member with respect to the slice.

        Note: When creating an SFA-style Slice Credential, the following roles typically allow users to operate at known GENI-compatible aggregates: "*" (asterisk) or the list of "refresh", "embed", "bind", "control" "info".

        Arguments:
          slice_urn: URN of slice for which to get member's credentials
          options: Potentially contains 'speaking-for' key indicating a speaks-for invocation (with certificate of the accountable member in the credentials argument)
        Return:
          List of credential in "CREDENTIALS" format, i.e. a list of credentials with type information suitable for passing to aggregates speaking AM API V3.
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def modify_slice_membership(slice_urn, credentials, options):
        """
        Modify slice membership, adding, removing and changing roles of members with respect to given slice

        Arguments:
          Slice_urn: URN of slice for which to modify membership
          Options:
              members_to_add: List of member_urn/role tuples for members to add to slice of form {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}
              members_to_remove: List of member_urn of members to remove from slice
              members_to_change: List of member_urn/role tuples for members whose role should change as specified for given slice of form {'SLICE_MEMBER' : member_urn, 'SLICE_ROLE' : role}

        Return:
          None
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_slice_members(slice_urn, credentials, options):
        """
        Lookup members of given slice and their roles within that slice
        
        Arguments:
          slice_urn: URN of slice for which to provide current members and roles
        
        Return:
           List of dictionaries of member_urn/role pairs [{'SLICE_MEMBER': member_urn, 'SLICE_ROLE': role }...] where 'role' is a string of the role name
        """

    def lookup_slices_for_member(member_urn, credentials, options):
        """
        Lookup slices for which the given member belongs

        Arguments:
          Member_urn: The member for whom to find slices to which it belongs

        Return:
           List of dictionary of slice_urn/role pairs [('SLICE_URN' : slice_urn, 'SLICE_ROLE' : role} ...] for each slice to which a member belongs, where role is a string of the role name
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def create_sliver_info(credentials, options):
        """
        Create a record of a sliver creation

        Arguments:
          options: 'fields' containing the fields for the sliver info  being registered at SA

        Return:
        Dictionary of name/value pairs for created sliver_info record
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def delete_sliver_info(sliver_urn, credentials, options):
        """Delete a sliver_info record

        Arguments:
           sliver_urn: urn of sliver whose record is to be deleted

        Return:
          True if succeeded

        Should return ARGUMENT_ERROR if no such sliver urn is registered
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def update_sliver_info(sliver_urn, credentials, options):
        """
        Update the details of a sliver_info record

        Arguments:
          sliver_urn: urn of sliver for which to update
          options: 'fields' containing fields for sliver_infos that are permitted for update

        Return:
          None

        Should return ARGUMENT_ERROR if no such sliver_urn is found
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_sliver_info(credentials, options):
        """
        Lookup sliver_info for given match criteria return fields in given filter criteria

        Arguments:
          options: 'match' for query match criteria, 'filter' for fields to be returned

        Return:
           Dictionary (indexed by sliver_urn) of dictionaries containing name/value pairs for all sliver_infos registered at this SA matching given criteria.
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def create_project(credentials, options):
        """
        Create project with given details. See generic create_* description above.

        Arguments:
          Options: 'fields', a dictionary of name/value pairs for newly created project.

        Return:
          Dictionary of name/value pairs of newly created project including urn

        Should return DUPLICATE_ERROR if creating a project for which a project of same name exists.
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_projects(credentials, options):
        """
        Lookup project detail for projects matching 'match options.
        'filter options indicate what detail to provide.

        Arguments:
           options: What details to provide (filter options) for which members (match options)

        Return:
           Dictionary of name/value pairs from 'filter' options for each project matching 'match' option criteria.
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def update_project(project_urn, credentials, options):
        """
        Update fields in given project object, as allowed in Get_version advertisement. See generic update_* description above.

        Arguments:
           project_urn: URN of project to update
           Options: Contains 'fields' key referencing dictionary of key/value pairs to update project

        Return: None
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def modify_project_membership(project_urn, credentials, options):
        """
        Modify project membership, adding, removing and changing roles of members with respect to given project

        Arguments:
          project_urn: Name of project for which to modify membership
          Options:
             members_to_add: List of member_urn/role tuples for members to add to project of form {'PROJECT_MEMBER': member_urn, 'PROJECT_ROLE' : role}
             members_to_remove: List of member_urn of members to remove from project
             members_to_change: List of member_urn/role tuples for members whose role should change as specified for given project of form {'PROJECT_MEMBER' : member_urn, 'PROJECT_ROLE' : role}

        Return:  None
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_project_members (project_urn, credentials, options):
        """
        Lookup members of given project and their roles within that project

        Arguments:
           project_urn: project_urn for which to provide current members and roles

        Return:
          List of dictionaries of member_urn/role pairs of form [{'PROJECT_MEMBER': member_urn, 'PROJECT_ROLE': role}...]
        """
        raise GFedv1NotImplementedError("Method not implemented")

    def lookup_projects_for_member(member_urn, credentials, options):
        """
        Lookup projects for which the given member belongs

        Arguments:
           Member_urn: The member for whom to find project to which it belongs

        Return:
           Dictionary of slice_urn/role pairs ('PROJECT_URN' : project_urn, 'PROJECT_ROLE' : role} where role is a string of the role name
        """
        raise GFedv1NotImplementedError("Method not implemented")
