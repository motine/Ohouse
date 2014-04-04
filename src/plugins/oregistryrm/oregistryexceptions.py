from amsoil.core.exception import CoreException
        
class ORegistryException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "ORegistry: %s" % (self._desc,)
