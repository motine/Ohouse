# import os, os.path
# from datetime import datetime
# from dateutil import parser as dateparser
# from lxml import etree

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('dhcpgeniv3delegate')

GENIv3DelegateBase = pm.getService('geniv3delegatebase')
exceptions = pm.getService('geniv3exceptions')

# from exceptions import *

class DHCPGENI3Delegate(GENIv3DelegateBase):
    """
    """
    
    def __init__(self):
        super(DHCPGENI3Delegate, self).__init__()
        pass
    
    # def get_request_extensions(self):
    #     """Documentation see [geniv3rpc]g3rpc/genivtrheehandler.GENIv3DelegateBase."""
    #     return ['http://example.com/dhcp/req.xsd'] # TODO remove and insert []
    # 
    # def get_ad_extensions(self):
    #     """Should retrun a list of request extensions (XSD schemas) to be sent back by GetVersion."""
    #     return ['http://example.com/dhcp/ad.xsd'] # TODO remove and insert []
    # 
    # def is_single_allocation(self):
    #     """Shall return a True or False. When True (not default), and performing one of (Describe, Allocate, Renew, Provision, Delete), such an AM requires you to include either the slice urn or the urn of all the slivers in the same state.
    #     see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#OperationsonIndividualSlivers"""
    #     # raise GENIv3DatabaseError("Some explaination or hint.")
    #     return False
    # 
    # def get_allocation_mode(self):
    #     """Shall return a either 'geni_single', 'geni_disjoint', 'geni_many'.
    #     It defines whether this AM allows adding slivers to slices at an AM (i.e. calling Allocate multiple times, without first deleting the allocated slivers).
    #     For description of the options see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#OperationsonIndividualSlivers"""
    #     return 'geni_single'
    # 
    def list_resources(self, client_cert, credentials, geni_available):
        """Documentation see [geniv3rpc]g3rpc/genivtrheehandler.GENIv3DelegateBase."""
        # check for geni_available
        return "<rspec>hallo</rspec>"
    # 
    # def describe(self, urns, client_cert, credentials):
    #     """Shall return an RSpec version 3 (manifest) or raise an GENIv3...Error.
    #     {urns} contains a list of slice identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    # 
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Describe"""
    #     return "<rspec>hallo 2</rspec>" # TODO remove and throw an error
    # 
    # def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
    #     """
    #     Shall return the two following values or raise an GENIv3...Error.
    #     - a RSpec version 3 (manifest) of newly allocated slivers 
    #     - a list of slivers of the format:
    #         [{'geni_sliver_urn' : String,
    #           'geni_expires'    : Python-Date,
    #           'geni_allocation_status' : one of the ALLOCATION_STATE_xxx}, 
    #          ...]
    #     Please return like so: "return respecs, slivers"
    #     {slice_urn} contains a slice identifier (e.g. 'urn:publicid:IDN+ofelia:eict:gcf+slice+myslice').
    #     {end_time} Optional. A python datetime object which determines the desired expiry date of this allocation (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#geni_end_time).
    #     >>> This is the first part of what CreateSliver used to do in previous versions of the AM API. The second part is now done by Provision, and the final part is done by PerformOperationalAction.
    #     
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Allocate"""
    #     return "<rspec>hallo 2</rspec>", [{'geni_sliver_urn' : "Sliver-URN", 'geni_expires'    : datetime(2013, 01, 24, 9, 30, 00),
    #           'geni_allocation_status' : self.ALLOCATION_STATE_ALLOCATED}] # TODO remove and throw an error
    # 
    # def renew(self, urns, client_cert, credentials, expiration_time, best_effort):
    #     """
    #     Shall return a list of slivers of the following format or raise an GENIv3...Error:
    #         [{'geni_sliver_urn'         : String,
    #           'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
    #           'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
    #           'geni_expires'            : Python-Date,
    #           'geni_error'              : optional String}, 
    #          ...]
    #     
    #     {urns} contains a list of slice identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    #     {expiration_time} is a python datetime object
    #     {best_effort} determines if the method shall fail in case that not all of the urns can be renewed (best_effort=False).
    # 
    #     If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv3OperationUnsupportedError.
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Renew"""
    #     return [{'geni_sliver_urn'         : "URNIIIIII",
    #           'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
    #           'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
    #           'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #           'geni_error'              : ""}] # TODO remove and throw an error
    # 
    # def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
    #     """
    #     Shall return the two following values or raise an GENIv3...Error.
    #     - a RSpec version 3 (manifest) of slivers 
    #     - a list of slivers of the format:
    #         [{'geni_sliver_urn'         : String,
    #           'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
    #           'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
    #           'geni_expires'            : Python-Date,
    #           'geni_error'              : optional String}, 
    #          ...]
    #     Please return like so: "return respecs, slivers"
    # 
    #     {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    #     {best_effort} determines if the method shall fail in case that not all of the urns can be provisioned (best_effort=False)
    #     {end_time} Optional. A python datetime object which determines the desired expiry date of this provision (see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#geni_end_time).
    #     {geni_users} is a list of the format: [ { 'urn' : ..., 'keys' : [sshkey, ...]}, ...]
    #     
    #     If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv3OperationUnsupportedError.
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Provision"""
    #     return "<rspec>hallo 3</rspec>", [{
    #                 'geni_sliver_urn'         : "Sliver-URN",
    #                 'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
    #                 'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
    #                 'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #                 'geni_error'              : ""}] # TODO remove and throw an error
    # 
    # def status(self, urns, client_cert, credentials):
    #     """
    #     Shall return the two following values or raise an GENIv3...Error.
    #     - a slice urn
    #     - a list of slivers of the format:
    #         [{'geni_sliver_urn'         : String,
    #           'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
    #           'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
    #           'geni_expires'            : Python-Date,
    #           'geni_error'              : optional String}, 
    #          ...]
    #     Please return like so: "return slice_urn, slivers"
    # 
    #     {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    #     
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Status"""
    #     return "Slice-URN", [{
    #                 'geni_sliver_urn'         : "asdas",
    #                 'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
    #                 'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
    #                 'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #                 'geni_error'              : ""}] # TODO remove and throw an error
    # 
    # def perform_operational_action(self, urns, client_cert, credentials, action, best_effort):
    #     """
    #     Shall return a list of slivers of the following format or raise an GENIv3...Error:
    #         [{'geni_sliver_urn'         : String,
    #           'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
    #           'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
    #           'geni_expires'            : Python-Date,
    #           'geni_error'              : optional String}, 
    #          ...]
    # 
    #     {urns} contains a list of slice or sliver identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    #     {action} an arbitraty string, but the following should be possible: "geni_start", "geni_stop", "geni_restart"
    #     {best_effort} determines if the method shall fail in case that not all of the urns can be changed (best_effort=False)
    # 
    #     If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv3OperationUnsupportedError.
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    #     
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#PerformOperationalAction"""
    #     return [{   'geni_sliver_urn'         : "asdas",
    #                 'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
    #                 'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
    #                 'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #                 'geni_error'              : ""}] # TODO remove and throw an error (unsupported)
    # 
    # def delete(self, urns, client_cert, credentials, best_effort):
    #     """
    #     Shall return a list of slivers of the following format or raise an GENIv3...Error:
    #         [{'geni_sliver_urn'         : String,
    #           'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
    #           'geni_expires'            : Python-Date,
    #           'geni_error'              : optional String}, 
    #          ...]
    # 
    #     {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    #     {best_effort} determines if the method shall fail in case that not all of the urns can be deleted (best_effort=False)
    #     
    #     If the transactional behaviour of {best_effort}=False can not be provided, throw a GENIv3OperationUnsupportedError.
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Delete"""
    #     return [{   'geni_sliver_urn'         : "asdas",
    #                 'geni_allocation_status'  : self.ALLOCATION_STATE_UNALLOCATED,
    #                 'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #                 'geni_error'              : ""}] # TODO remove and throw an error (unsupported)
    # 
    # def shutdown(self, slice_urn, client_cert, credentials):
    #     """
    #     Shall return True or False or raise an GENIv3...Error.
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Shutdown"""
    #     return True # TODO remove and throw an error