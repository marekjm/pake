#!/usr/bin/env python3

"""This module contains data shared between pake.transactions.* modules.
"""

# List of subkeywords for PAKE meta-language statements
#
#   ('KEYWORD', 'request_name', int(number_of_arguments), [list,of,conflicting,keywords])

statement_subkeywords_for_pkg = [('PKG', 'req', 0, []),
                                 ('FETCH', 'fetch', 1, ['REMOVE', 'INSTALL']),
                                 ('REMOVE', 'remove', 1, ['FETCH', 'INSTALL']),
                                 ('INSTALL', 'install', 1, ['REMOVE', 'FETCH']),
                                 ('VERSION', 'version', 1, ['INSTALL']),
                                 ('FROM', 'origin', 1, ['REMOVE', 'INSTALL']),
                                ]
