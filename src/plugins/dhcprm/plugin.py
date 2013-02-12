import amsoil.core.pluginmanager as pm

from dhcpresourcemanager import DHCPResourceManager
import dhcpexceptions as exceptions_package

def setup():
    # setup config keys
    config = pm.getService("config")
    config.install("dhcprm.max_reservation_duration", 10*60, "Maximum duration a DHCP resource can be held allocated (not provisioned).")
    config.install("dhcprm.max_lease_duration", 24*60*60, "Maximum duration DHCP lease can be provisioned.")
    config.install("geniv3rpc.rspec_validation", True, "Determines if RSpec shall be validated by the given xs:schemaLocations in the document (may cause downloads of the given schema from the given URL per request).")
    
    rm = DHCPResourceManager()
    pm.registerService('dhcpresourcemanager', rm)
    pm.registerService('dhcpexceptions', exceptions_package)
    