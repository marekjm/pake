### PAKE 

PAKE is a distributed system for distribution of Python source modules.

However, it doesn't operate on *Python-specific* files only and can be used to distribute any kind of
data - let it be text files, binary files and whatever you may throw at it.  
Data is transferred in `*.tar.xz` archieves which are created using JSON configuration files. 

----

### Installation

Well, this is kinda embarassing that a package management system is not bale to install itself but
I'm working on this issue.

For now, the only installation method is with `Makefile` located in repo.

PAKE backend will be installed in `$PYTHON_SITEPACKAGES/pake`.
PAKE UI logic code will be installed in `$BINDIR/`.
JSON descriptions of PAKE UI will be stored in `$SHAREDIR/pake/ui`.

Check `Makefile` for the default values of these variables.
If you can run `make install` and get no errors you can be 99% sure that PAKE will be working.


Basic rules are that backend should be installed inside your Python `site-packages` directory,
UI logic should be installed in any directory in your `PATH` and runnable by your user.

UI descriptions can be installed in two directories and be found by PAKE:

* `/usr/share/pake/ui`,
* `~/.local/share/pake/ui`.

Different locations requires you to tinker with code of `getuipath()` function (it can be found in `pake/shared.py` module)
which iterates over a list of directoriesto find one containing PAKE data.
