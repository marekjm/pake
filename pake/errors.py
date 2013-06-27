class NodeError(Exception):
    """Generic exception for node-related operations.
    """
    pass


class DuplicateError(Exception):
    """Exception raised when trying to add a node duplicate.
    """
    pass


class PackageError(Exception):
    """Generic exception for package-related operations.
    """
    pass
