import logging

class CoreException(Exception):
  def __init__ (self):
    self._logged = False

  def log(self, logh, msg, level = logging.ERROR):
    logh.log(level, msg)
    self._logged = True


#Derived exceptions
class ConfigExceptions(CoreException):
    def __init__(self, desc):
        self._desc = desc

    def __str__(self):
        return "Configuration: %s" % (self._desc,)

class NotImplementedError(CoreException):
    pass
class NoProviderAvailableError(CoreException):
    pass


class MissingFileOrData(ConfigExceptions):
    def __init__(self, path_value):
        super(MissingFileOrData,self).__init__("File in %s is missing or file data is malformed" %path_value)
