#!/usr/bin/env python3

"""This module contains data shared between pake.transactions.* modules.
"""

# List of subkeywords for PAKE meta-language statements
#
#   ('KEYWORD', 'request_name', int(number_of_arguments), [list,of,conflicting,keywords])

fetch_statement_subkeywords =  [('FETCH', 'name', 1), ('VERSION', 'version', 1), ('FROM', 'origin', 1)]
install_statement_subkeywords = [('INSTALL', 'name', 1), ('VERSION', 'version', 1)]
remove_statement_subkeywords = [('REMOVE', 'name', 1)]
meta_statement_subkeywords = [('NODE', 'node', 0), ('META', 'action', 1), ('KEY', 'key', 1), ('VALUE', 'value', 1)]


statement_subkeywords_for_pkg = [('PKG', 'req', 0, []),
                                 ('FETCH', 'fetch', 1, ['REMOVE', 'INSTALL']),
                                 ('REMOVE', 'remove', 1, ['FETCH', 'INSTALL']),
                                 ('INSTALL', 'install', 1, ['REMOVE', 'FETCH']),
                                 ('VERSION', 'version', 1, ['INSTALL']),
                                 ('FROM', 'origin', 1, ['REMOVE', 'INSTALL']),
                                ]
statement_subkeywords_for_node = []
statement_subkeywords_for_nest = []
