from amsoil.core.exception import CoreException

class DelegateToolsException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "DelegateTools: %s" % (self._desc,)

class ConfigFileMissing(DelegateToolsException):
    def __init__(self, path):
        super(ConfigFileMissing, self).__init__("Config file could not be found (%s)" % (path,))

class MalformedConfigFile(DelegateToolsException):
    def __init__(self, path, comment):
        super(MalformedConfigFile, self).__init__("Malformed JSON in the config file (%s): %s" % (path, comment))
