## Definitions

* `global repository` - local repository which contains node metadata, subdirectories for projects,
    list of all known nodes etc.,
* `sub-repository` - repository for single project containing its metadata and archieves,
* `node` - global repository uploaded to server,


## Quick guide to usage

Basic tools are already available. 
One thing you can do is to create a node. 
Since no official, unified interface has been created you have to use 
scripts written for testing.

    python3 pake-setup.py --verbose
    python3 pake-meta.py --missing --verbose

The second call will give you an overview of keys you must set.

    python3 pake-meta.py --set author "Joe"
    python3 pake-meta.py --set url http://pake.example.com
    python3 pake-meta.py --set push-url example.com
    python3 pake-meta.py --set contact "joe [at] example [dot] com"

If everything went OK you can push your node.

    python3 pake-push.py

If you have to change directory after logging in to the server use `-R` option.

    python3 pake-push.py --verbose -R "/domains/example.com/public_html/pake"

If you want to store your authentication data (**warning!**: this data are stored in plaintext 
in the `~/.pakenode/.authfile` file on you computer, the `pake` will not ever do anything with them 
except for reading and writing them to this file on login so if your machine is protected you can use the switches).
To store auth data you can use either `--store-auth` or `-s` options, to use stored data use `--use-auth` or `-u`.

    python3 pake-push.py --verbose --store-auth

After first push you can create fallback files, just in case the future uploads will encounter some problems. 
This is enabled with `--create-fallback` option.
What I would recommend is:

    python3 pake-push.py --verbose --store-auth --dont-push
    python3 pake-push.py --verbose --use-auth -R "/your/path"
    python3 pake-push.py --verbose -u -R "/your/path" --create-fallback


----

## Repositories

`pake` has two types of repository -- global (located in the user's home directory) and 
local (located in any directory the user wants). 

These repositories are created using different commands (as discused below) and have different characteristics.


#### Global repository

This repository MUST BE located in user's home directory in `~/.pakenode` subdirectory.

This repository is uploaded onto the server and acts as a *node*. 
It is created using `pake setup` command.

    ~/.pakenode/
        meta.json
        nodes.json
        packages.json
        installed.json
        prepared.json       # this file is a list of transactions prepared offline and 
                            # not yet commited
        
        db/
            * directory to which `packages.json` files from nodes are downloaded
            * they are stored here so transactions can be prepared offline and 
            * commited when a connection to the Internet is available
            
        downloaded/
            * directory to which archieves are downloaded*
            
        installing/
            * directory to which contents of archieves are extracted before installing*

        prepared/
            [hash].json     # this is file describing a transaction prepared offline and 
                            # waiting for being commited
        
        packages/
            foo/
                meta.json
                * this directory reflects contents of `versions/` subdirectory of a project*
                foo-0.0.1.json
                foo-0.0.1.tar.xz
                foo-0.0.2.json
                foo-0.0.2.tar.xz


----


#### Sub-repository

This repository can be located in ANY directory in `.pake` subdirectory.

This repository contains one project.
It is created using `pake init`. 

    ./.pake/
        meta.json 
            *this meta contains name of the project e.g. `foo` which is used as a name for subdirectory in ~/.pakenode/packages/,
             is also a meta for newest version*
             
        versions/
            foo-0.0.1.json
            foo-0.0.1.tar.xz
            foo-0.0.2.json
            foo-0.0.2.tar.xz


----


## Setup

#### Node setup

To set up a node you have to own a server on which the node can be uploaded. 
No special environment is needed as in `pake` everything is done locally and 
servers on the Internet are used only for storage and create a network (but clients 
run only on users' computers).

This requires proper setup from the very beginning.

----

##### Files of the node


These files should always be available on the node's server. 
If they are not, `fallback.*` files should be checked. 
Fallback files are not always present, they are created when a user does runs 
`python pake-push.py` with either `--create-fallback` or `-F` options.


###### `meta.json`

Most important file in EVERY node is `meta.json` -- if this cannot be downloaded a node is considered dead to rest of the network. 
If `meta.json` is present but incomplete (which means it does not contains all required keys) node is also considered dead.

Minimal contents of `meta.json` of a *living* node are:

    {
        'author':'Joe Example',
        'contact':'email [at] example [dot] com',
        'url':'http://pake.example.com/',
        'push-url':'example.com',
    }

`author` key is used to store authors name or nick. 
`contact` is necessary for contacting author is something is wrong with the node. 
`url` is main URL of the node,
`push-url` is the URL used to push data to the node,

>   **Detail**: if you set up a mirror for your node do not put its URL in `url` field -- leave it in `mirrors`.
>   This way `pake` can determine if it is using a mirror or the original repository.

----

###### `mirrors.json`

This file lists all mirrors for the node.

Example contents:

        [
            'http://pake.example.com',
            'https://pakenode.foo.net',
            'ftp://pake.bar.net',
        ]

Every element of the list MUST BE a URL.

----

###### `nodes.json`

This file contains a list. Every element of the list is a `meta.json` file with 
additional key `mirrors` (which is created from `mirrors.json` file) for a different node. 

Example `nodes.json` file:

    [
        {
            'author':'Joe Example',
            'contact':'email [at] example [dot] com',
            'url':'http://pake.example.com/',
            'mirrors':[],
        },
        {
            'author':'Bill Przykladsky',
            'contact':'bill [at] przykladsky [dot] net',
            'url':'http://pake.przykladsky.net/',
            'mirrors':['http://pake.przykladsky.com'],
        }
    ]

If the file cannot be downloaded from the node it is assumed that the file is empty list 
(so the node cannot be used for node discovery) and is a dead end of the network.

----

###### `packages.json`

This file contains a list. Every element of the list is a `meta.json` file for a different package.

If the file cannot be downloaded from the node it is assumed that the file is empty list (so the node has no packages of itself). 
Such nodes can be set up by people who are not distributing any content but are providing a *discovery-nodes* for the network -- 
then they should contain as many nodes as possible for they are as valuable as their node lists.

----

###### `installed.json`

Is a list of all packages installed via `pake` (is very similar to `packages.json` in its contents). 
Uploading this file to the net is *optional* because it can be useful for crackers who 
might want to know what stuff do you have installed on your system but at the same time can be used for backups -- 
by reading it `pake` can recreate your environment.


----

#### Sub-repository initialization


##### Files of the sub-directory

This files are placed in sub-repository (one that name is `.pake`).

----

###### `meta.json`

It is the same as in `meta.json` file for the node -- most important file.
If it does not contain required keys the package is considered broken.

Example file:

    {
        'name':'foo',
        'version':'0.0.1',
        'license':'GNU GPL v2+/GNU GPL v3+',
        'url':'http://pake.example.com',
        'dependencies':[],
    }

Explanations:

*   `name` - name of the package,
*   `version` - version of the package, must be valid semver string,
*   `license` - (can be left blank but must be present) name of the license used for this package,
*   `url` - main url from where the package can be downloaded,
*   `dependencies` - list of dependencies the package requires,

Optional keys are:

*   `author` - if it is not found `pake` will take author of the repository as the author of the package,
*   `keywords` - list of keywords used by search feature; if not found keywords are extracted from `name` and `description`,
*   `description` - description of the package,
*   `module-name` - if different from package name (you are discouraged from designing such packages),


Every element in `dependencies` is a dict:
    
    {
        'name':'foo',
        'min':'0.3.16', // optional
        'max':'0.5.0', // optional
        'url':'http://pake.example.com/', // optional but SHOULD be present, if is not found pake will try to determine its url
    }

----

###### `INSTALL`

This is install script which is interpreted by a pake installer. 
We don't use shell scripts because they can contain malicious code. 
Installer, however, have very small set of rules which can be used (see: Installing: Rules).

----

###### `foo-0.0.1.tar.xz`

Archieve containg `INSTALL` and `REMOVE` scripts and package files.
Filename explained: `[package name]-[version].tar.xz`

----


## Packages

#### Installing

Process of installation is controlled by `INSTALL` script. 
If the script is empty (or not found) all contents of `installing` directory are 
copied to `site-packages` subdirectory named after the package.

##### Rules

Rules that can be used in installation scripts are:

*   `MKDIR`
*   `CP`
*   `ECHO`

Install environment is closed by what I mean that no file operations can be done except 
copying files and making directories and these actions may only take 
place in current working directory and `site-packages` directory.

Few examples:

    MKDIR $/foo
    CP __init__.py $/foo/__init__.py

This would make directory `foo` in `site-packages` directory and copy `__init__.py` from 
current working directory (`.`) to it.
`$` character means *`site-packages` directory*.


Algorythm:

0.  `pake` will define base for transaction,
1.  `pake` will list all dependencies required for transaction,
2.  if dependencies cannot be satisfied because of version issues abort with a message informing about it,
3.  if dependencies cannot be satisfied because they were not found in network abort and suggest using repo discovery,
4.  repeat steps `1.` through `3.` until all dependencies are satisfied,
5.  check if dependencies match set filters (like license, max version or whaterver will be implemented),
6.  `pake` will try to find mirrors for every pakcage in transaction,
7.  `pake` will determine main url for every package in transaction,
8.  download all packages,
9.  define order of installation,
10. extract first package to `~/.pakenode/installing/`,
11. run `INSTALL` script,
12. clean `~/.pakenode/installing/`,
13. remove first item from list of packages to install,
14. repeat setps `11.` through `14.` for all packages,


----

#### Searching

You can search for packages using `pake search keyword...` feature.
Installation is done via `pake install PACKAGE...` command.

>   **Detail:** transactions could be represented `Transaction()` objects,
>   then they can be exported to JSON and stored, repeated, undo-ed and so on,
>   we can even have history of transactions,

    Transaction():
        packages = [{'name':'', 'url':'', 'mirrors':[], 'dependencies':[]}]
        type = ''
        
        commit(): commits the transaction
        resolve(): checks dependencies
        order(): set packages in order of dependencies
        download():
        install(): run `INSTALL` script
        size(): returns size of transaction


----

Protocol version: 0.0.5+20130627
