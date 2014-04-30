from amsoil.core.exception import CoreException

class GFedv1BaseError(CoreException):
    def __init__(self, code, name, description, comment):
        self.code = code
        self.name = name
        self.description = description
        self.comment = comment

    def __str__(self):
        return "[%s] %s (%s)" % (self.name, self.description, self.comment)

class GFedv1AuthenticationError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 1, 'AUTHENTICATION_ERROR', "The invoking tool or member did not provide appropriate credentials indicating that they are known to the CH or that they possessed the private key of the entity they claimed to be.", comment)
class GFedv1AuthorizationError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 2, 'AUTHORIZATION_ERROR', "The invoking tool or member does not have the authority to invoke the given call with the given arguments.", comment)
class GFedv1ArgumentError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 3, 'ARGUMENT_ERROR', "The arguments provided to the call were mal-formed or mutually inconsistent.", comment)
class GFedv1DatabaseError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 4, 'DATABASE_ERROR', "An error from the underlying database was returned.", comment) # (More info should be provided in the 'output' return value)
class GFedv1NotImplementedError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(100, 'NOT_IMPLEMENTED_ERROR', "The given method is not implemented on the server.", comment)
class GFedv1ServerError(GFedv1BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(101, 'SERVER_ERROR', "An error in the client/server connection", comment)
