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
