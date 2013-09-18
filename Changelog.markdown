## PAKE changelog

This file is a history of changes done to PAKE.
It started to gather information after version `0.0.16`.


----

#### Version `0.1.0` (2013-09-):

PAKE repositories were renamed to nests. It severes two purposes at once:
removes confusion about the word *repository* and
acts as a nice language hack (snakes have nests and Python is a snake).

Methods of config objects were adapted to create more fluent API where it made sense (not in getters, `__list__`, etc.).


* __upd__:  `write()` must be explicitly called on `Config()` objects,
* __upd__:  `pake.shared.getrootpath()` renamed to `getnodepath()`,
* __upd__:  `pake.shared.getrepopath()` renamed to `getnestpath()`,
* __upd__:  `pake.repository.*` moved to `pake.nest.*`,
* __upd__:  `pake.config.node.Registered` renamed to `pake.config.node.Nests`,


----


#### Version 0.0.16 (2013-08-17):

__rem__:    `RELEASE.md` file is removed,

__new__:    `ui/node` can add, remove and list alien nodes,
