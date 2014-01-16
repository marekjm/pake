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
    def __init__(self, root, requests=[]):
        """
        :param root: directory that transactions are run in
        :param requests: list of requests
        """
        self._root = root
        self._reqs = requests
        self._stack = []

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
        elif action == 'node.manager.reinit':
            confpath = os.path.join(req['path'], '.pakenode')
            meta = pake.config.node.Meta(confpath)
            nests = pake.config.node.Nests(confpath)
            pushers = pake.config.node.Pushers(confpath)
            aliens = pake.config.network.Aliens(confpath)
            self._executenode('node.manager.remove', {'path': req['path']})
            self._executenode('node.manager.init', {'path': req['path']})
            meta.write()
            nests.write()
            pushers.write()
            aliens.write()
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
        elif action == 'node.config.meta.reset':
            pake.config.node.Meta(os.path.join(root, '.pakenode')).reset().write()
        elif action == 'node.config.mirrors.set':
            pake.config.node.Pushers(os.path.join(root, '.pakenode')).set(**req).write()
        elif action == 'node.config.mirrors.get':
            self._stack.append(pake.config.node.Pushers(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'node.config.mirrors.remove':
            pake.config.node.Pushers(os.path.join(root, '.pakenode')).remove(**req).write()
        elif action == 'node.config.mirrors.geturls':
            self._stack.append(pake.config.node.Pushers(os.path.join(root, '.pakenode')).geturls())
        elif action == 'node.config.mirrors.genlist':
            pake.node.pusher.genmirrorlist(os.path.join(root, '.pakenode'))
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
        elif action == 'node.push':
            req['root'] = os.path.join(root, '.pakenode')
            pake.node.pusher.push(**req)
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
        elif action == 'nest.build':
            pake.nest.package.build(root=os.path.join(root, '.pakenest'), version=req['version'])
        else:
            self._issueunknown(action, fatalwarns)

    def _executenetwork(self, action, request, fatalwarns=False):
        """Execute network-related requests.
        """
        req = request
        root = self._root
        if action == 'network.aliens.set':
            req['alien'] = {}
            if 'mirrors' in req:
                req['alien']['mirrors'] = req['mirrors']
                del req['mirrors']
            if 'meta' in req:
                req['alien']['meta'] = req['meta']
                del req['meta']
            alien = pake.network.aliens.manager.set(os.path.join(root, '.pakenode'), **req)
            self._stack.append(alien)
        elif action == 'network.aliens.get':
            self._stack.append(pake.config.network.Aliens(os.path.join(root, '.pakenode')).get(**req))
        elif action == 'network.aliens.geturls':
            self._stack.append(pake.config.network.Aliens(os.path.join(root, '.pakenode')).urls())
        elif action == 'network.aliens.getall':
            self._stack.append(pake.config.network.Aliens(os.path.join(root, '.pakenode')).all())
        elif action == 'network.aliens.remove':
            pake.config.network.Aliens(os.path.join(root, '.pakenode')).remove(**req).write()
        else:
            self._issueunknown(action, fatalwarns)

    def execute(self, req, fatalwarns=False):
        """This is used to execute single requests.
        """
        call = req['call']
        if 'params' in req: params = req['params']
        else: params = {}
        if call.split('.')[0] == 'node': self._executenode(call, params, fatalwarns)
        elif call.split('.')[0] == 'nest': self._executenest(call, params, fatalwarns)
        elif call.split('.')[0] == 'network': self._executenetwork(call, params, fatalwarns)
        else: self._issueunknown(call, fatalwarns)
        return self

    def run(self, fatalwarns=False):
        """Call this method to run the transaction.
        """
        for req in self._reqs: self.execute(req, fatalwarns)
        return self

    def getstack(self):
        """Returns stack of the transaction.
        """
        return self._stack
