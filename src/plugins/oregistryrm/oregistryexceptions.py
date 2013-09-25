from amsoil.core.exception import CoreException
        
class ORegistryException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "ORegistry: %s" % (self._desc,)

class RegistryConfigFileMissing(ORegistryException):
    def __init__(self, path):
        super(RegistryConfigFileMissing, self).__init__("Config file could not be found (%s)" % (path,))

class RegistryMalformedConfigFile(ORegistryException):
    def __init__(self, path, comment):
        super(RegistryMalformedConfigFile, self).__init__("Malformed JSON in the config file (%s): %s" % (path, comment))
