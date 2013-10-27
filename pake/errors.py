class PAKEError(Exception):
    """Generic class for all PAKE related exceptions.
    """
    pass


class NodeError(PAKEError):
    """Generic exception for node-related operations.
    """
    pass


class DuplicateError(PAKEError):
    """PAKEError raised when trying to add a node duplicate.
    """
    pass


class PackageError(PAKEError):
    """Generic exception for package-related operations.
    """
    pass


class EncodingError(PAKEError):
    """Exception raised by encoder when it does not know how to encode a statement.
    """
    pass


class NotAFileError(PAKEError):
    """Raised when trying to add something that is not a file to the list of files
    of the nest.
    """
    pass
