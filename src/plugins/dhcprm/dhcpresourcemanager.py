from datetime import datetime, timedelta

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('dhcpresourcemanager')

from dhcpexceptions import *

class DHCPResourceManager(object):
    config = pm.getService("config")
    
    RESERVATION_TIMEOUT = config.get("dhcprm.max_reservation_duration") # sec
    MAX_LEASE_DURATION = config.get("dhcprm.max_lease_duration") # sec

    
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
    
    def free_lease(self, lease):
        lease = self._find_by_ip(lease['ip']) # find the internal data object
        lease['slice_name'] = None
        lease['owner_uuid'] = None
        lease['owner_email'] = None
        lease['end_time'] = None
        
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


    def test_remove_me(self, params):
        logger.info("I was called with %s" % (params, ))