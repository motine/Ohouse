# import os, os.path
from datetime import datetime, timedelta
# from dateutil import parser as dateparser
# from lxml import etree

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('dhcpgeniv3delegate')

GENIv3DelegateBase = pm.getService('geniv3delegatebase')
exceptions = pm.getService('geniv3exceptions')

# from exceptions import *

from amsoil.core.exception import CoreException

class DHCPException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "DHCP: %s" % (self._desc,)

class DHCPLeaseNotFound(DHCPException):
    def __init__(self, ip):
        super(DHCPLeaseNotFound, self).__init__("Lease not found (%s)" % (ip,))

class DHCPLeaseAlreadyTaken(DHCPException):
    def __init__(self, ip):
        super(DHCPLeaseAlreadyTaken, self).__init__("Lease is already taken (%s)" % (ip,))

class DHCPMaxLeaseDurationExceeded(DHCPException):
    def __init__(self, ip):
        super(DHCPMaxLeaseDurationExceeded, self).__init__("Desired lease duration is too far in the future (%s)" % (ip,))


class DHCPResourceManager(object):
    RESERVATION_TIMEOUT = 10*60 # sec
    MAX_LEASE_DURATION = 24*60*60 # sec
    
    # TODO implement cron job to expire leases
    
    def __init__(self):
        super(DHCPResourceManager, self).__init__()
        self._leases = []
        for i in range(1,20):
            self._leases.append({'ip' : ("192.168.1.%i" % (i,)), 'slice_name' : None, 'owner_uuid' : None, 'owner_email' : None, 'end_time' : None})
    
    def get_all_leases(self):
        return self._leases[:]
    
    def reserve_lease(self, ip, slice_name, owner_uuid, owner_email=None, end_time=None):
        lease = self._find_by_ip(ip)
        if (lease['slice_name']): # do checking if ip is already taken
            raise DHCPLeaseAlreadyTaken(ip)

        # change database entry
        lease['slice_name'] = slice_name
        lease['owner_uuid'] = owner_uuid
        lease['owner_email'] = owner_email
        self._set_end_time(lease, end_time, self.RESERVATION_TIMEOUT)
        return lease
    
    def extend_lease(self, lease, end_time=None):
        lease = self._find_by_ip(lease['ip']) # find the internal data object
        self._set_end_time(lease, end_time, self.MAX_LEASE_DURATION)
    
    def leases_in_slice(self, slice_name):
        return filter(lambda lease: (lease['slice_name'] == slice_name), self._leases)
    
    def is_occupied(self, lease):
        return bool(lease['slice_name'])
    
    def lease_for_ip(self, ip):
        """Retrieves a value object which contains the lease for the given {ip}."""
        return self._find_by_ip(ip).copy()

    def _find_by_ip(self, ip):
        for lease in self._leases:
            if lease['ip'] == ip:
                return lease
        raise DHCPLeaseNotFound(ip)

    def _set_end_time(self, lease, end_time, max_duration):
        """If {end_time} is none, the current time+{max_duration} is assumed."""
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise DHCPMaxLeaseDurationExceeded(lease['ip'])
        lease['end_time'] = end_time
        
class DHCPGENI3Delegate(GENIv3DelegateBase):
    """
    """
    
    URN_PREFIX = 'urn:DHCP_AM' # TODO should also include a changing component, identified by a config key
    
    def __init__(self):
        super(DHCPGENI3Delegate, self).__init__()
        self._resource_manager = DHCPResourceManager() # TODO get from pm
    
    def get_request_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dhcp' : 'http://example.com/dhcp'} # /request.xsd
    
    def get_manifest_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dhcp' : 'http://example.com/dhcp'} # /manifest.xsd
    
    def get_ad_extensions_mapping(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        return {'dhcp' : 'http://example.com/dhcp'} # /ad.xsd
    
    def is_single_allocation(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        We allow to address single slivers (IPs) rather than the whole slice at once."""
        return False
    def get_allocation_mode(self):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        We allow to incrementally add new slivers (IPs)."""
        return 'geni_many'

    def list_resources(self, client_cert, credentials, geni_available):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        self.auth(client_cert, credentials, None, ('listslices',))
        
        root_node = self.lxml_ad_root()
        E = self.lxml_ad_element_maker('dhcp')
        
        for lease in self._resource_manager.get_all_leases():
            is_taken = self._resource_manager.is_occupied(lease)
            if is_taken and geni_available: continue # take care of geni_available
            r = E.resource()
            r.append(E.available("False" if is_taken else "True"))
            # possible to list other properties
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
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""

        client_urn, client_uuid, client_email = self.auth(client_cert, credentials, slice_urn, ('createsliver',))
        
        requested_ips = []
        # parse RSpec -> requested_ips
        rspec_root = self.lxml_parse_rspec(rspec)
        for elm in rspec_root.getchildren():
            if not self.lxml_elm_has_request_prefix(elm, 'dhcp'):
                raise exceptions.GENIv3BadArgsError("RSpec contains elements/namespaces I dont understand (%s)." % (elm,))
            if (self.lxml_elm_equals_request_tag(elm, 'dhcp', 'ip')):
                requested_ips.append(elm.text.strip())
            elif (self.lxml_elm_equals_request_tag(elm, 'dhcp', 'iprange')):
                pass
                # raise exceptions.GENIv3GeneralError('IP ranges in RSpecs are not supported yet.') # TODO
            else:
                raise exceptions.GENIv3BadArgsError("RSpec contains an element I dont understand (%s)." % (elm,))
        
        reserved_leases = []
        for rip in requested_ips:
            try:
                reserved_leases.append(self._resource_manager.reserve_lease(rip, slice_urn, client_uuid, client_email, end_time))
            except DHCPLeaseNotFound as e: # translate the resource manager exceptions to GENI exceptions
                raise exceptions.GENIv3SearchFailedError("The desired IP(s) could no be found (%s)." % (rip,))
            except DHCPLeaseAlreadyTaken as e:
                raise exceptions.GENIv3BusyError("The desired IP(s) is already taken (%s)." % (rip,))
            
        # assemble sliver list
        sliver_list = []
        for lease in reserved_leases:
            sliver_list.append(self._get_sliver_status_hash(lease))
        return self.lxml_to_string(self._get_manifest_rspec(reserved_leases)), sliver_list

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
    #     sliver_list.append(self._get_sliver_status_hash_for_lease(lease), True, True, "")
    #     return [{'geni_sliver_urn'         : "URNIIIIII",
    #           'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
    #           'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
    #           'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
    #           'geni_error'              : ""}] # TODO remove and throw an error
    # 
    def provision(self, urns, client_cert, credentials, best_effort, end_time, geni_users):
        """Documentation see [geniv3rpc] GENIv3DelegateBase.
        {geni_users} is not relevant here."""
        
        # TODO honor best_effort
        provisioned_leases = []
        
        for urn in urns:
            if (self.urn_type(urn) == 'slice'):
                client_urn, client_uuid, client_email = self.auth(client_cert, credentials, urn, ('createsliver',)) # authenticate for each given slice
                leases = self._resource_manager.leases_in_slice(urn)
                for lease in leases: # extend the lease, so we have a longer timeout.
                    self._resource_manager.extend_lease(lease, end_time)
                # usually you would really instanciate resources here (not necessary for IP-resources)
                provisioned_leases.extend(leases)
            else:
                raise exceptions.GENIv3OperationUnsupportedError('Only slice URNs can be provisioned by this aggregate')
        
        if len(provisioned_leases) == 0:
            raise exceptions.GENIv3BadArgsError("There are no resources in the given slice(s)")
        # assemble return values
        sliver_list = []
        for lease in provisioned_leases:
            sliver_list.append(self._get_sliver_status_hash(lease, True, True, ""))

        return self.lxml_to_string(self._get_manifest_rspec(provisioned_leases)), sliver_list

        # involved_slices = []
        # for urn in urns:
        #     try:
        #         lease = self._resource_manager.lease_for_ip(self._urn_to_ip(urn))
        #         involved_slices.append(lease['slice_name'])
        #         raise RuntimeError(lease['owner_uuid'])
        #     except DHCPLeaseNotFound as e:
        #         raise exceptions.GENIv3SearchFailedError("There is no IP for the given urn (%s)." % (urn,))
        # for slice_urn in involved_slices:
        #     client_urn, client_uuid, client_email = self.auth(client_cert, credentials, slice_urn, ('createsliver',))
        
        # check if all urns have been allocated
        #
        # TODO USE _urn_to_ip helper method

    
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
    #     sliver_list.append(self._get_sliver_status_hash_for_lease(lease), True, True, "")
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
    #     sliver_list.append(self._get_sliver_status_hash_for_lease(lease), True, True, "")
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
    def shutdown(self, slice_urn, client_cert, credentials):
        """Documentation see [geniv3rpc] GENIv3DelegateBase."""
        # client_urn, client_uuid, client_email = self.auth(client_cert, credentials, slice_urn, ('shutdown',))
        raise exception.GENIv3GeneralError("Method not implemented")
        return True
    
    def _ip_to_urn(self, ip):
        """Helper method to map IPs to URNs."""
        return ("%s:%s" % (self.URN_PREFIX, ip.replace('.', '-')))
    def _urn_to_ip(self, urn):
        """Helper method to map URNs to IPs."""
        if (urn.startswith(self.URN_PREFIX)):
            return urn[len(self.URN_PREFIX)+1:].replace('-', '.')
        else:
            raise exceptions.GENIv3BadArgsError("The given URN is not valid for this AM (%s)" %(urn,))

    def _get_sliver_status_hash(self, lease, include_allocation_status=False, include_operational_status=False, error_message=None):
        """Helper method to create the sliver_status return values of allocate and other calls."""
        result = {'geni_sliver_urn' : self._ip_to_urn(lease['ip']),
                  'geni_expires'    : lease['end_time'],
                  'geni_allocation_status' : self.ALLOCATION_STATE_ALLOCATED}
        result['geni_allocation_status'] = self.ALLOCATION_STATE_PROVISIONED if self._resource_manager.is_occupied(lease) else self.ALLOCATION_STATE_UNALLOCATED
        if (include_operational_status): # there is no state to an ip, so we always return ready
            result['geni_operational_status'] = self.OPERATIONAL_STATE_READY
        if (error_message):
            result['geni_error'] = error_message
        return result

    def _get_manifest_rspec(self, leases):
        E = self.lxml_manifest_element_maker('dhcp')
        manifest = self.lxml_manifest_root()
        sliver_list = []
        for lease in leases:
            # assemble manifest
            r = E.resource()
            r.append(E.ip(lease['ip']))
            # TODO add more info here
            manifest.append(r)
        return manifest
        
