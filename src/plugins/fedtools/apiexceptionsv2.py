from amsoil.core.exception import CoreException

class GFedv2BaseError(CoreException):
    def __init__(self, code, name, description, comment):
        self.code = code
        self.name = name
        self.description = description
        self.comment = comment

    def __str__(self):
        return "[%s] %s (%s)" % (self.name, self.description, self.comment)

class GFedv2AuthenticationError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 1, 'AUTHENTICATION_ERROR', "The invoking tool or member did not provide appropriate credentials indicating that they are known to the CH or that they possessed the private key of the entity they claimed to be.", comment)
class GFedv2AuthorizationError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 2, 'AUTHORIZATION_ERROR', "The invoking tool or member does not have the authority to invoke the given call with the given arguments.", comment)
class GFedv2ArgumentError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 3, 'ARGUMENT_ERROR', "The arguments provided to the call were mal-formed or mutually inconsistent.", comment)
class GFedv2DatabaseError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__( 4, 'DATABASE_ERROR', "An error from the underlying database was returned.", comment)
class GFedv2DuplicateError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(5, 'DUPLICATE_ERROR', "An error indicating attempt to create an object that already exists", comment)
class GFedv2NotImplementedError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(100, 'NOT_IMPLEMENTED_ERROR', "The given method is not implemented on the server.", comment)
class GFedv2ServerError(GFedv2BaseError):
    def __init__(self, comment):
        super(self.__class__, self).__init__(101, 'SERVER_ERROR', "An error in the client/server connection", comment)

