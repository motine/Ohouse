import os, os.path
from datetime import datetime
from dateutil import parser as dateparser
# from lxml import etree

import ext.geni
import ext.sfa.trust.gid as gid

import amsoil.core.pluginmanager as pm
from amsoil.core import serviceinterface
import amsoil.core.log
logger=amsoil.core.log.getLogger('geniv3handler')

from exceptions import *

xmlrpc = pm.getService('xmlrpc')

class GENIv3Handler(xmlrpc.Dispatcher):
    # TODO
    # """This class implements all GENI methods and delegates these to the adapters registered with the adapter registry, but only to the adapters which implement GENI2AdapterBase.
    # 
    # Please find the API documentation via the GENI wiki: http://groups.geni.net/geni/wiki/GAPI_AM_API_V2
    # 
    # Authentication pseudocode:
    #     st = pm.getService('contextstorage')
    #     user_id = getOrCreateUserIdFromThisPluginsDatabase(user_urn) # returns GUID which has been saved to this thread's database
    #     st['user'] = getContextObjFromAuthorziation(user_id) # this will get persisted
    #     st['user_info'] = { ... } # this not persisted
    #     st['request_data'] = { post_data, certs, ... }
    # """
    
    RFC3339_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f%z'
    
    def __init__(self):
        super(GENIv3Handler, self).__init__(logger)
        self._delegate = None
    
    @serviceinterface
    def setDelegate(self, geniv3delegate):
        self._delegate = geniv3delegate
    
    @serviceinterface
    def getDelegate(self):
        return self._delegate


    # RSPEC3_NAMESPACE= 'http://www.geni.net/resources/rspec/3'
    
    def GetVersion(self):
        """Returns the version of this interface.
        This method can be hard coded, since we are actually setting up the GENI v3 API, only.
        For the RSpec extensions, we ask the delegate."""
        # no authentication necessary
        
        try:
            request_extensions = self._delegate.get_request_extensions()
            ad_extensions = self._delegate.get_ad_extensions()
            single_allocation = 1 if self._delegate.get_sliver_allocation_mode() else 0
        except Exception as e:
            return self._errorReturn(e)
                
        request_rspec_versions = [
            { 'type' : 'geni', 'version' : '3', 'schema' : 'http://www.geni.net/resources/rspec/3/request.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/3', 'extensions' : request_extensions},]
        ad_rspec_versions = [
                { 'type' : 'geni', 'version' : '3', 'schema' : 'http://www.geni.net/resources/rspec/3/ad.xsd', 'namespace' : 'http://www.geni.net/resources/rspec/3', 'extensions' : ad_extensions },]
        credential_types = { 'geni_type' : 'geni_sfa', 'geni_version' : '3' }
    
        return self._successReturn({ 
                'geni_api'                    : '3',
                'geni_api_versions'           : { '3' : '/RPC2' }, # FIXME this should be an absolute URL
                'geni_request_rspec_versions' : request_rspec_versions,
                'geni_ad_rspec_versions'      : ad_rspec_versions,
                'geni_credential_types'       : credential_types,
                'geni_single_allocation'      : single_allocation,
                'geni_allocate'               : 'geni_many'
                })

    def ListResources(self, credentials, options):
        """Delegates the call and unwraps the needed parameter. Also takes care of the compression option."""
        # interpret options
        geni_available = bool(options['geni_available']) if ('geni_available' in options) else False
        geni_compress = bool(options['geni_compress']) if ('geni_compress' in options) else False

        # check version and delegate
        try:
            self._checkRSpecVersion(options['geni_rspec_version'])
            result = self._delegate.list_resources(credentials, geni_available)
        except Exception as e:
            return self._errorReturn(e)
        # compress and return
        if geni_compress:
            result = base64.b64encode(zlib.compress(result))
        return self._successReturn(result)

    def Describe(self, urns, credentials, options):
        """Delegates the call and unwraps the needed parameter. Also takes care of the compression option."""
        # some duplication with above
        geni_compress = bool(options['geni_compress']) if ('geni_compress' in options) else False

        try:
            self._checkRSpecVersion(options['geni_rspec_version'])
            result = self._delegate.describe(urns, credentials)
        except Exception as e:
            return self._errorReturn(e)

        if geni_compress:
            result = base64.b64encode(zlib.compress(result))
        return self._successReturn(result)

    def Allocate(self, slice_urn, credentials, rspec, options):
        """Delegates the call and unwraps the needed parameter. Also converts the incoming timestamp to python and the outgoing to geni compliant date format."""
        geni_end_time = self._str2datetime(options['geni_end_time']) if ('geni_end_time' in options) else None
        
        try:
            # delegate
            result_rspec, result_sliver_list = self._delegate.allocate(slice_urn, credentials, rspec, geni_end_time)
            # change datetime's to strings
            result = { 'geni_rspec' : result_rspec, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def Renew(self, urns, credentials, expiration_time_str, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else True
        expiration_time = self._str2datetime(expiration_time_str)
        try:
            # delegate
            result = self._delegate.renew(urns, credentials, expiration_time, geni_best_effort)
            # change datetime's to strings
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)
    
    def Provision(self, urns, credentials, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else True
        geni_end_time = self._str2datetime(options['geni_end_time']) if ('geni_end_time' in options) else None
        geni_users = options['geni_users'] if ('geni_users' in options) else []
        
        try:
            self._checkRSpecVersion(options['geni_rspec_version'])
            result_rspec, result_sliver_list = self._delegate.provision(urns, credentials, geni_best_effort, geni_end_time, geni_users)
            result = { 'geni_rspec' : result_rspec, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)
    
    def Status(self, urns, credentials, options):
        try:
            result_sliceurn, result_sliver_list = self._delegate.status(urns, credentials)
            result = { 'geni_urn' : result_sliceurn, 'geni_slivers' : self._convertExpiresDate(result_sliver_list) }
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def PerformOperationalAction(self, urns, credentials, action, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else False
        try:
            result = self._delegate.perform_operational_action(urns, credentials, action, geni_best_effort)
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def Delete(self, urns, credentials, options):
        geni_best_effort = bool(options['geni_best_effort']) if ('geni_best_effort' in options) else False
        try:
            result = self._delegate.delete(urns, credentials, geni_best_effort)
            result = self._convertExpiresDate(result)
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)

    def Shutdown(self, slice_urn, credentials, options):
        try:
            result = bool(self._delegate.shutdown(slice_urn, credentials))
        except Exception as e:
            return self._errorReturn(e)
        return self._successReturn(result)


    # ---- helper methods
    def _datetime2str(self, dt):
        return dt.strftime(self.RFC3339_FORMAT_STRING)
    def _str2datetime(self, strval):
        return dateparser.parse(strval)

    def _convertExpiresDate(self, sliver_list):
        for slhash in sliver_list:
            if not isinstance(slhash['geni_expires'], datetime):
                raise ValueError("Given geni_expires in sliver_list hash retrieved from delegate's method is not a python datetime object.")
            slhash['geni_expires'] = self._datetime2str(slhash['geni_expires'])
        return sliver_list

    def _checkRSpecVersion(self, rspec_version_option):
        if (int(rspec_version_option['version']) != 3) or (rspec_version_option['type'].lower() != 'geni'):
            raise GENIv3BadArgsError("Only RSpec 3 supported.")
        
    def _errorReturn(self, e):
        """Assembles a GENI compliant return result for faulty methods."""
        if not isinstance(e, GENIv3BaseError): # convert common errors into GENIv3GeneralError
            e = GENIv3GeneralError(str(e))
        return { 'geni_api' : 3, 'code' : { 'geni_code' : e.code }, 'output' : str(e) }
        
    def _successReturn(self, result):
        """Assembles a GENI compliant return result for successful methods."""
        return { 'geni_api' : 3, 'code' : { 'geni_code' : 0 }, 'value' : result, 'output' : None }



class GENIv3DelegateBase(object):
    """The GENIv3 handler assumes that this class uses RSpec version 3 when interacting with the client."""
    
    ALLOCATION_STATE_UNALLOCATED = 'geni_unallocated'
    ALLOCATION_STATE_ALLOCATED = 'geni_allocated'
    ALLOCATION_STATE_PROVISIONED = 'geni_provisioned'

    OPERATIONAL_STATE_PENDING_ALLOCATION = 'geni_pending_allocation'
    OPERATIONAL_STATE_NOTREADY           = 'geni_notready'
    OPERATIONAL_STATE_CONFIGURING        = 'geni_configuring'
    OPERATIONAL_STATE_STOPPING           = 'geni_stopping'
    OPERATIONAL_STATE_READY              = 'geni_ready'
    OPERATIONAL_STATE_READY_BUSY         = 'geni_ready_busy'
    OPERATIONAL_STATE_FAILED             = 'geni_failed'

    def __init__(self):
        super(GENIv3DelegateBase, self).__init__()
        pass
    
    def get_request_extensions(self):
        """Should retrun a list of request extensions (XSD schema URLs as string) to be sent back by GetVersion."""
        return ['http://example.com/dhcp/req.xsd'] # TODO remove and insert []
    
    def get_ad_extensions(self):
        """Should retrun a list of request extensions (XSD schemas) to be sent back by GetVersion."""
        return ['http://example.com/dhcp/ad.xsd'] # TODO remove and insert []
    
    def get_sliver_allocation_mode(self):
        # raise GENIv3DatabaseError("Some explaination or hint.")
        return True

    def list_resources(self, credentials, geni_available):
        """Shall return an RSpec version 3 (advertisement) or raise an GENIv3...Error.
        If {geni_available} is set, only return availabe resources.
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#ListResources"""
        return "<rspec>hallo</rspec>" # TODO remove and throw an error

    def describe(self, urns, credentials):
        """Shall return an RSpec version 3 (manifest) or raise an GENIv3...Error.
        {urns} contains a list of slice identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Describe"""
        return "<rspec>hallo 2</rspec>" # TODO remove and throw an error

    def allocate(self, slice_urn, credentials, rspec, geni_end_time=None):
        """
        Shall return the two following values or raise an GENIv3...Error.
        - a RSpec version 3 (manifest) of newly allocated slivers 
        - a list of slivers of the format:
            [{'geni_sliver_urn' : String,
              'geni_expires'    : Python-Date,
              'geni_allocation_status' : one of the ALLOCATION_STATE_xxx}, 
             ...]
        Please return like so: "return respecs, slivers"
        {slice_urn} contains a slice identifier (e.g. 'urn:publicid:IDN+ofelia:eict:gcf+slice+myslice').
        >>> This is the first part of what CreateSliver used to do in previous versions of the AM API. The second part is now done by Provision, and the final part is done by PerformOperationalAction.
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Allocate"""
        return "<rspec>hallo 2</rspec>", [{'geni_sliver_urn' : "Sliver-URN", 'geni_expires'    : datetime(2013, 01, 24, 9, 30, 00),
              'geni_allocation_status' : self.ALLOCATION_STATE_ALLOCATED}] # TODO remove and throw an error

    def renew(self, urns, credentials, expiration_time, best_effort):
        """
        Shall return a list of slivers of the following format or raise an GENIv3...Error:
            [{'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...]
        
        {urns} contains a list of slice identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {expiration_time} is a python datetime object
        {best_effort} determines if the method shall fail in case that not all of the urns can be renewed (best_effort=False)
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Renew"""
        return [{'geni_sliver_urn'         : "URNIIIIII",
              'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
              'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
              'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
              'geni_error'              : ""}] # TODO remove and throw an error

    def provision(self, urns, credentials, best_effort, end_time, geni_users):
        """
        Shall return the two following values or raise an GENIv3...Error.
        - a RSpec version 3 (manifest) of slivers 
        - a list of slivers of the format:
            [{'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...]
        Please return like so: "return respecs, slivers"

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {best_effort} determines if the method shall fail in case that not all of the urns can be provisioned (best_effort=False)
        {end_time} is a python datetime object
        {geni_users} is a list of the format: [ { 'urn' : ..., 'keys' : [sshkey, ...]}, ...]
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Provision"""
        return "<rspec>hallo 3</rspec>", [{
                    'geni_sliver_urn'         : "Sliver-URN",
                    'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
                    'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
                    'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
                    'geni_error'              : ""}] # TODO remove and throw an error

    def status(self, urns, credentials):
        """
        Shall return the two following values or raise an GENIv3...Error.
        - a slice urn
        - a list of slivers of the format:
            [{'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...]
        Please return like so: "return slice_urn, slivers"

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Status"""
        return "Slice-URN", [{
                    'geni_sliver_urn'         : "asdas",
                    'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
                    'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
                    'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
                    'geni_error'              : ""}] # TODO remove and throw an error

    def perform_operational_action(self, urns, credentials, action, best_effort):
        """
        Shall return a list of slivers of the following format or raise an GENIv3...Error:
            [{'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_operational_status' : one of the OPERATIONAL_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...]

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {action} an arbitraty string, but the following should be possible: "geni_start", "geni_stop", "geni_restart"
        {best_effort} determines if the method shall fail in case that not all of the urns can be changed (best_effort=False)
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#PerformOperationalAction"""
        return [{   'geni_sliver_urn'         : "asdas",
                    'geni_allocation_status'  : self.ALLOCATION_STATE_ALLOCATED,
                    'geni_operational_status' : self.OPERATIONAL_STATE_PENDING_ALLOCATION,
                    'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
                    'geni_error'              : ""}] # TODO remove and throw an error (unsupported)

    def delete(self, urns, credentials, best_effort):
        """
        Shall return a list of slivers of the following format or raise an GENIv3...Error:
            [{'geni_sliver_urn'         : String,
              'geni_allocation_status'  : one of the ALLOCATION_STATE_xxx,
              'geni_expires'            : Python-Date,
              'geni_error'              : optional String}, 
             ...]

        {urns} contains a list of slice/resource identifiers (e.g. ['urn:publicid:IDN+ofelia:eict:gcf+slice+myslice']).
        {best_effort} determines if the method shall fail in case that not all of the urns can be deleted (best_effort=False)
        
        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Delete"""
        return [{   'geni_sliver_urn'         : "asdas",
                    'geni_allocation_status'  : self.ALLOCATION_STATE_UNALLOCATED,
                    'geni_expires'            : datetime(2013, 01, 24, 9, 30, 00),
                    'geni_error'              : ""}] # TODO remove and throw an error (unsupported)

    def shutdown(self, slice_urn, credentials):
        """
        Shall return True or False or raise an GENIv3...Error.

        For full description see http://groups.geni.net/geni/wiki/GAPI_AM_API_V3#Shutdown"""
        return True # TODO remove and throw an error

