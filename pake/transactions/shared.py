#!/usr/bin/env python3

"""This module contains data shared between pake.transactions.* modules.
"""

# List of subkeywords for PAKE meta-language statements
#
# These lists MUST contain only two-tuples.
# These two-tuples MUST come in the following form:
#
#   ('SOURCECODE_NAME', 'middle_form_name')
#
# First element is looked for in the parsed source code lines and
# second is used when translating lines into middle-form undesrstood
# by interpreter.
# Similarly, when encoding back to source code, second element is looked for in
# middle-form dict and first is used when SUBKEYWORD is inserted into source code
# being created.
#
# First element of the list of subkeywords must be main keyword of the statement.
# It is used to determine name of the package (for INSTALL, REMOVE and FETCH statements),
# action to perform (for META, NEST, ALIEN and MIRROR statements).

fetch_statement_subkeywords =  [('FETCH', 'name'), ('VERSION', 'version'), ('FROM', 'origin')]
install_statement_subkeywords = [('INSTALL', 'name'), ('VERSION', 'version')]
remove_statement_subkeywords = [('REMOVE', 'name')]
meta_statement_subkeywords = [('META', 'action'), ('KEY', 'key'), ('VALUE', 'value')]
