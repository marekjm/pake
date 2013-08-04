### PAKE 

By design, PAKE is a distributed system for distribution of Python source modules.

However, it doesn't operate on *Python-specific* files only and can be used to distribute any kind of
data - let it be text files, binary files and whatever you may throw at it.  
Data is transferred in `*.tar.xz` archieves which are created using JSON configuration files. 

----

### Introduction

Few words of explanation about PAKE terminology.

#### Nodes

Your local node is located in '~/.pakenode` directory. It contains all registered packages, configuration files and 
directories used for cache and during installation. 

To create a node visible to other users of the network you must have access to an FTP server. 
If you do, creating a mirror is as easy as creating a *pusher* (small dictionary containing information how to push data
to this server) and calling `pakenode push` from the command line. 

To expand your network you must add new nodes to your `nodes.json` configuration file. This is as simple as adding node's URL
to this file.

----

#### Repositories

Repository, in PAKE meaning, is local directory containing information about a package. It is contained in a directory
named `.pake`.

When repository is created it *is NOT* automaticaly added to the node database - it must be *registered*. 
This allows you to create packages using PAKE and distribute them using different system. 

----

### Usage

Every program in PAKE toolchain has few options which provide you with the ability to set their level of
verbosity. You can combine them to get different results, depending on what do you wnat in particular situation.

*   `-V`, `--verbose`:      make PAKE display more messages about what it is doing,
*   `-Q`, `--quiet`:        make PAKE display no messages about what it is doing,
*   `-D`, `--debug`:        make PAKE display debug messages (combine this option with `--quiet` to get pure debugging logs),

Programs in PAKE toolchain operate on modes. This means that usually one program can do different things and what it *will* do
is controlled by passing a mode definition (`init`, `meta`, `mirrors`, etc.). Also, mode describes what options program can
take at the moment so read `--help` messages for each of the tools you'll be using with PAKE.

PAKE employs CLAP library to build its user interface. It allows passing global options, such as these above, before or
after a mode definition.


#### Creating a node

To create a node use this command:

    pakenode init

If you want to check if your environment allows you to perform such an action use `--dry-run` option.

    pakenode init --dry-run


#### Creating a repository

    pakerepo init --name "foo"
    pakerepo files --add --regexp '*\.py$' .
    pakerepo meta --version '0.0.1'
    pakerepo package --build


#### Adding repository to node's database

    pakenode packages --register /home/user/path/to/package

Where `/home/user/path/to/package` is a directory containing `.pake` directory.
PAKE will return an error if repository contains malformed or incomplete `meta.json` file.
