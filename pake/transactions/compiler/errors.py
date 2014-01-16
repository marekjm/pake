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
    pass


class UndefinedConstantError(MetalError):
    pass


class ConstantRedefinitionError(MetalError):
    pass


class InvalidCallError(MetalError):
    pass


class CompilationError(MetalError):
    pass
