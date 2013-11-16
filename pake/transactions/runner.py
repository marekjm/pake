#!/sur/bin/env python3

"""This file contains PAKE transactions runner.
"""


import os
import warnings

import pake


class Runner():
    """This object implements logic needed to run PAKE
    requests - request is a middle-form of a single line of
    transaction file.
    """
    def __init__(self, root, requests):
        """
        :param root: directory that transactions are run in
        :param requests: list of requests
        """
        self._root = root
        self._reqs = requests
        self._stack = []

    def finalize(self):
        """Finalize data in the transaction e.g. fill missing data.
        """
        return self

    def _issueunknown(self, action, fatalwarns):
        """Deals with unknown action.
        """
        if fatalwarns: raise pake.errors.UnknownRequestError(action)
        else: warnings.warn('unknown action: {0}'.format(action))

    def _executenode(self, action, request, fatalwarns=False):
        """Executes transactions for node.*
        """
        req = request
        root = self._root
        if action == 'node.manager.init':
            pake.node.manager.makedirs(req['path'])
            pake.node.manager.makeconfig(req['path'])
        elif action == 'node.manager.remove':
            pake.node.manager.remove(req['path'])
        elif action == 'node.config.meta.set':
            pake.config.node.Meta(os.path.join(root, '.pakenode')).set(**req).write()
        elif action == 'node.config.meta.get':
            self._stack.append(pake.config.node.Meta(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'node.config.meta.remove':
            pake.config.node.Meta(os.path.join(root, '.pakenode')).remove(**req).write()
        elif action == 'node.config.meta.getkeys':
            self._stack.append(pake.config.node.Meta(os.path.join(root, '.pakenode')).keys())
        elif action == 'node.config.mirrors.set':
            pake.config.node.Pushers(os.path.join(root, '.pakenode')).set(**req).write()
        elif action == 'node.config.mirrors.get':
            self._stack.append(pake.config.node.Pushers(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'node.config.mirrors.remove':
            pake.config.node.Pushers(os.path.join(root, '.pakenode')).remove(**req).write()
        elif action == 'node.config.mirrors.genlist':
            pake.node.pusher.genmirrorlist(os.path.join(root, '.pakenode'))
        elif action == 'node.config.aliens.set':
            pake.config.node.Aliens(os.path.join(root, '.pakenode')).set(**req).write()
        elif action == 'node.config.aliens.get':
            self._stack.append(pake.config.node.Aliens(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'node.config.aliens.geturls':
            self._stack.append(pake.config.node.Aliens(os.path.join(root, '.pakenode')).urls())
        elif action == 'node.config.aliens.getall':
            self._stack.append(pake.config.node.Aliens(os.path.join(root, '.pakenode')).all())
        elif action == 'node.config.aliens.remove':
            pake.config.node.Aliens(os.path.join(root, '.pakenode')).remove(**req).write()
        elif action == 'node.config.nests.register':
            pake.node.packages.register(root=os.path.join(root, '.pakenode'), path=req['path'])
        elif action == 'node.config.nests.get':
            self._stack.append(pake.config.node.Nests(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'node.config.nests.getpaths':
            self._stack.append(pake.config.node.Nests(os.path.join(root, '.pakenode')).paths())
        elif action == 'node.config.nests.remove':
            pake.config.node.Nests(os.path.join(root, '.pakenode')).remove(**req).write()
        elif action == 'node.packages.genlist':
            pake.node.packages.genpkglist(os.path.join(root, '.pakenode'))
        else:
            self._issueunknown(action, fatalwarns)

    def _executenest(self, action, request, fatalwarns=False):
        """Executes transactions for nest.*
        """
        req = request
        root = self._root
        if action == 'nest.manager.init':
            pake.nest.manager.makedirs(req['path'])
            pake.nest.manager.makeconfig(req['path'])
        elif action == 'nest.manager.remove':
            pake.nest.manager.remove(root)
        elif action == 'nest.config.meta.set':
            pake.config.nest.Meta(os.path.join(root, '.pakenest')).set(**req).write()
        elif action == 'nest.config.meta.remove':
            pake.config.nest.Meta(os.path.join(root, '.pakenest')).remove(**req).write()
        elif action == 'nest.config.versions.add':
            pake.config.nest.Versions(os.path.join(root, '.pakenest')).add(**req).write()
        elif action == 'nest.config.versions.remove':
            pake.config.nest.Versions(os.path.join(root, '.pakenest')).remove(**req).write()
        elif action == 'nest.config.dependencies.set':
            pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).set(**req).write()
        elif action == 'nest.config.dependencies.get':
            self._stack.append(pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).get(**req))
        elif action == 'nest.config.dependencies.update':
            pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).update(**req).write()
        elif action == 'nest.config.dependencies.remove':
            pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).remove(**req).write()
        elif action == 'nest.config.dependencies.getnames':
            self._stack.append(list(pake.config.nest.Dependencies(os.path.join(root, '.pakenest'))))
        elif action == 'nest.config.dependencies.list':
            depconf = pake.config.nest.Dependencies(os.path.join(root, '.pakenest'))
            deps = []
            for i in list(depconf):
                dep = depconf.get(i)
                dep['name'] = i
                deps.append(dep)
            self._stack.append(deps)
        elif action == 'nest.config.files.add':
            pake.config.nest.Files(os.path.join(root, '.pakenest')).add(**req).write()
        elif action == 'nest.config.files.remove':
            pake.config.nest.Files(os.path.join(root, '.pakenest')).remove(**req).write()
        elif action == 'nest.config.files.list':
            self._stack.append(list(pake.config.nest.Files(os.path.join(root, '.pakenest'))))
        else:
            self._issueunknown(action, fatalwarns)

    def run(self, fatalwarns=False):
        """Call this method to run the transaction.
        """
        for req in self._reqs:
            action = req['act']
            del req['act']
            root = self._root
            if action.split('.')[0] == 'node': self._executenode(action, req, fatalwarns)
            elif action.split('.')[0] == 'nest': self._executenest(action, req, fatalwarns)
            else: self._issueunknown(action, fatalwarns)
        return self

    def getstack(self):
        """Returns stack of the transaction.
        """
        return self._stack
