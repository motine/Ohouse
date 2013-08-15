from amsoil.core.exception import CoreException
        
class OCHException(CoreException):
    def __init__(self, desc):
        self._desc = desc
    def __str__(self):
        return "OCH: %s" % (self._desc,)

class CHConfigFileMissing(OCHException):
    def __init__(self, path):
        super(CHConfigFileMissing, self).__init__("Config file could not be found (%s)" % (path,))

class CHMalformedConfigFile(OCHException):
    def __init__(self, path, comment):
        super(CHMalformedConfigFile, self).__init__("Malformed JSON in the config file (%s): %s" % (path, comment))
