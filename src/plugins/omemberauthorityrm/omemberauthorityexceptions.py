from amsoil.core.exception import CoreException
        
class OMemberAuthorityException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "OMemberAuthority: %s" % (self._desc,)
