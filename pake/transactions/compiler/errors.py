#!/usr/bin/env python3

"""This file contains exceptions that can be raised by Akemetal.
"""


class MetalError(Exception):
    """This is base exception for all PyMetal related errors.
    Programs which aim to catch generic errors should look out for this
    exception.
    """
    pass


class UndeclaredReferenceError(MetalError):
    """Raised when a reference to an undeclared name if found.
    """
    pass


class UndefinedConstantError(MetalError):
    """Raised e.g. when const is compiled with undefined reference.
    """
    pass


class ConstantRedefinitionError(MetalError):
    """Raised when redefinition of a const value is found.
    """
    pass


class CompilationError(MetalError):
    pass
