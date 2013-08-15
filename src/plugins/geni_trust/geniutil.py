from ext.geni.util.urn_util import URN
from amsoil.core import serviceinterface

@serviceinterface
def decode_urn(urn):
    """Returns authority, type and name associated with the URN as string.
    example call:
      authority, typ, name = decode_urn("urn:publicid:IDN+eict.de+user+motine")
    """
    urn = URN(urn=str(urn))
    return urn.getAuthority(), urn.getType(), urn.getName() 

@serviceinterface
def encode_urn(authority, typ, name):
    """
    Returns a URN string with the given {authority}, {typ}e and {name}.
    {typ} shall be either of the following: authority, slice, user, sliver, (project or meybe others: http://groups.geni.net/geni/wiki/GeniApiIdentifiers#Type)
    example call:
      urn_str = encode_urn("eict.de", "user", "motine")
    """
    return URN(authority=authority, type=typ, name=name).urn_string()
