from amsoil.core.exception import CoreException
        
class OSliceAuthorityException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "OSliceAuthority: %s" % (self._desc,)
