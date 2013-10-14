### Transactions

Transactions are files containing rules.
They are usually created and interpreted by PAKE but can be written by
users/developers (for example `install`, `update` and `remove` transactions).

Transactions take form of plain text files with `.transaction` extension.


----

#### General transactions

General transactions arw written and interpreted by PAKE.


    # get a package or
    # fail if package does not exist
    GET foo-bar


    # get a specified version of a package or
    # fail if package does not exist
    GET foo-bar-0.0.1-alpha.3.rc.7


    # extract package contents to ~/.pakenode/installing/ or
    # fail if a directory is not empty or
    # fail if package is not found in ~/.pakenode/cache
    LOAD foo-bar

    # extract contents of specified version of a package to ~/.pakenode/installing/ or
    # fail if a directory is not empty or
    # fail if package is not found in ~/.pakenode/cache
    LOAD foo-bar-0.0.1-alpha.3.rc.7


    # install loaded package by running
    # `install.transaction` file from ~/.pakenode/installing/install.transaction
    INSTALL


    # remove a package
    REMOVE foo-bar


    # update a package or
    # fail if a package wasn't previously installed
    UPDATE foo-bar


----

#### File transactions

Transactions operating on files.

    # NOTICE about using relative paths
    #
    # Relative paths use *current working directory* as a starting point.
    # It's not entirely true for relative paths in PAKE transaction files.
    #
    # Here, you have to remember that all paths are expanded to absolute
    # before any action actually takes place and
    # that the starting point of relative paths is ~/.pakenode/installing
    # which is the directory to which packages are extracted.

    # NOTICE about sandboxing
    #
    # PAKE comes with a predefined but user-customizable file (allowed_actions.json)
    # describing which actions can be taken in which directories to prevent
    # damaging actions being commited by malicious scripts or
    # by accident
    #
    # RULES
    #
    # To allow an action to be taken in all directories use: "/" because
    # priviledges are given to all subdirectories of given directory.
    #
    # To prevent action from being taken in a subdirectory use "!/usr/bin"
    #
    # To allow action in no directory use empty list.
    #
    # Use only absolute paths.
    #
    # Rules are treated like regular expressions.
    # Every rule is expanded this way:
    #
    #   ^RULE
    #
    # and then compiled.


For more information about file-transactions refer to [FSRL](https://github.com/marekjm/pyfsrl) project.

----

#### Sandboxing of file-transactions

    {
        "cp": ["/"],
        "rm": ["."],
        "mv": ["."],
        "mkd": ["/"],
        "mkds": ["/"],
        "rmd": ["."],
        "rmtree": ["."]
    }
