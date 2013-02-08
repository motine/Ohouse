# import os, os.path
from datetime import datetime
# from dateutil import parser as dateparser
# from lxml import etree

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('dhcpgeniv3delegate')

GENIv3DelegateBase = pm.getService('geniv3delegatebase')
exceptions = pm.getService('geniv3exceptions')

# from exceptions import *

from amsoil.core.exception import CoreException

class DHCPLeaseNotFound(CoreException):
    def __init__(self, ip):
        self._ip = ip

    def __str__(self):
        return "DHCP lease not found (%s)" % (self._ip,)


class DHCPResourceManager(object):
    def __init__(self):
        super(DHCPResourceManager, self).__init__()
        self._leases = []
        for i in range(1,20):
            self._leases.append({'ip' : ("192.168.88.%i" % (i,)), 'slice_name' : None, 'owner_uuid' : None, 'owner_email' : None, 'timeout' : None})
    
    def get_all_leases(self):
        return self._leases[:]
    
    def reserve_lease(self, ip, slice_name, owner_uuid, owner_email=None, timeout=None):
        lease = self._find_by_ip(ip)
        # do checking if ip is already taken
        lease['slice_name'] = slice_name
        lease['owner_uuid'] = owner_uuid
        lease['owner_email'] = owner_email
        lease['timeout'] = timeout
        return lease
        
    def _find_by_ip(self, ip):
        for lease in self._leases:
            if lease['ip'] == ip:
                return lease
        raise DHCPLeaseNotFound(ip)
        
        
class DHCPGENI3Delegate(GENIv3DelegateBase):
    """
    """
    
    def __init__(self):
        super(DHCPGENI3Delegate, self).__init__()
        self._resource_manager = DHCPResourceManager() # TODO get from pm
    
    def get_request_extensions_list(self):
        """Documentation see GENIv3DelegateBase."""
        return ['http://example.com/dhcp/req.xsd']
    
    def get_manifest_extensions_mapping(self):
        """Documentation see GENIv3DelegateBase."""
        return {'dhcp' : 'http://example.com/dhcp/req.xsd'}
    
    def get_ad_extensions_mapping(self):
        """Documentation see GENIv3DelegateBase."""
        return {'dhcp' : 'http://example.com/dhcp/ad.xsd'}
    
    def is_single_allocation(self):
        """Documentation see GENIv3DelegateBase.
        We allow to address single slivers (IPs) rather than the whole slice at once."""
        return False
    def get_allocation_mode(self):
        """Documentation see GENIv3DelegateBase.
        We allow to incrementally add new slivers (IPs)."""
        return 'geni_many'

    def list_resources(self, client_cert, credentials, geni_available):
        """Documentation see [geniv3rpc]g3rpc/genivtrheehandler.GENIv3DelegateBase."""
        self.auth(client_cert, credentials, None, ('listslices',))
        
        root_node = self.lxml_ad_root()
        E = self.lxml_ad_element_maker('dhcp')
        
        # TODO check for geni_available (reduce result with list comprehension)
        for lease in self._resource_manager.get_all_leases():
            r = E.resource()
            r.append(E.available("False" if lease['slice_name'] else "True"))
            # TODO list other properties
            r.append(E.ip(lease['ip']))
            root_node.append(r)
        
        return self.lxml_to_string(root_node)
    
    # def describe(self, urns, client_cert, credentials):
    #     """Shall return an RSpec version 3 (manifest) or raise an GENIv3...Error.
    #     {urns} contains a list of slice identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
    # 
    #     For more information on possible {urns} see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3/CommonConcepts#urns
    # 
    #     For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Describe"""
    #     return "<rspec>hallo 2</rspec>" # TODO remove and throw an error

    def allocate(self, slice_urn, client_cert, credentials, rspec, end_time=None):
        """Documentation see [geniv3rpc]g3rpc/genivtrheehandler.GENIv3DelegateBase."""

        client_urn, client_uuid, client_email = self.auth(client_cert, credentials, None, ('createsliver',))
        
        # TODO validate RSpec
        # TODO parse RSpec -> requested_ips
        requested_ips = ['192.168.88.2', '192.168.88.3']
        
        # TODO catch _ResourceManager_-sepecific errors and translate them to GENI errors.
        try:
            reserved_ips = []
            for rip in requested_ips:
                # TODO change the timeout to 10 min or the end_time
                reserved_ips.append(self._resource_manager.reserve_lease(rip, slice_urn, client_uuid, client_email, end_time))
        except DHCPLeaseNotFound as e: # translate the resource manager exceptions to GENI exceptions
            raise exceptions.GENIv3SearchFailedError("The desired IP(s) could no be found")
            
        # assemble return values
        E = self.lxml_manifest_element_maker('dhcp')
        manifest = self.lxml_manifest_root()
        sliver_list = []
        for lease in reserved_ips:
            # assemble manifest
            r = E.resource()
            r.append(E.ip(lease['ip']))
            manifest.append(r)
            
            # assemble sliver list
            sliver_status = {'geni_sliver_urn' : ("urn:this_am:%s" % (lease['ip'],)), # TODO do a reasonable mapping here (should be done in this class)
                             'geni_expires'    : datetime(2013, 03, 24, 9, 30, 00),
                             'geni_allocation_status' : self.ALLOCATION_STATE_ALLOCATED}
            sliver_list.append(sliver_status)

        return self.lxml_to_string(manifest), sliver_list

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