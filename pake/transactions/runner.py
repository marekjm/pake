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
        """:param path: directory that transactions are run in (can be overridden by setting 'path' for individual requests)
        :param requests: list of requests
        """
        self._root = root
        self._reqs = requests

    def finalize(self):
        """Finalize data in the transaction e.g. fill missing data.
        """
        return self

    def run(self):
        """Call this method to run the transaction.
        """
        for req in self._reqs:
            action = req['act']
            del req['act']
            root = self._root
            if action == 'node.manager.init':
                pake.node.manager.makedirs(root)
                pake.node.manager.makeconfig(root)
            elif action == 'node.manager.remove':
                pake.node.manager.remove(req['path'])
            elif action == 'node.config.meta.set':
                pake.config.node.Meta(os.path.join(root, '.pakenode')).set(req['key'], req['value']).write()
            elif action == 'node.config.meta.remove':
                pake.config.node.Meta(os.path.join(root, '.pakenode')).remove(req['key']).write()
            elif action == 'node.config.mirrors.set':
                pake.config.node.Pushers(os.path.join(root, '.pakenode')).set(url=req['url'], host=req['host'], cwd=req['cwd']).write()
            elif action == 'node.config.mirrors.remove':
                pake.config.node.Pushers(os.path.join(root, '.pakenode')).remove(url=req['url']).write()
            elif action == 'node.config.aliens.set':
                pake.config.node.Aliens(os.path.join(root, '.pakenode')).set(url=req['url'], mirrors=req['mirrors'], meta=req['meta']).write()
            elif action == 'node.config.aliens.remove':
                pake.config.node.Aliens(os.path.join(root, '.pakenode')).remove(url=req['url']).write()
            elif action == 'node.config.nests.register':
                pake.node.packages.register(root=os.path.join(root, '.pakenode'), path=req['nestpath'])
            elif action == 'node.config.nests.remove':
                pake.config.node.Nests(os.path.join(root, '.pakenode')).remove(url=req['url']).write()
            elif action == 'nest.manager.init':
                pake.nest.manager.makedirs(req['path'])
                pake.nest.manager.makeconfig(req['path'])
            elif action == 'nest.manager.remove':
                pake.nest.manager.remove(req['path'])
            elif action == 'nest.config.meta.set':
                pake.config.nest.Meta(os.path.join(root, '.pakenest')).set(req['key'], req['value']).write()
            elif action == 'nest.config.meta.remove':
                pake.config.nest.Meta(os.path.join(root, '.pakenest')).remove(req['key']).write()
            elif action == 'nest.config.versions.add':
                pake.config.nest.Versions(os.path.join(root, '.pakenest')).add(**req).write()
            elif action == 'nest.config.versions.remove':
                pake.config.nest.Versions(os.path.join(root, '.pakenest')).remove(**req).write()
            elif action == 'nest.config.dependencies.set':
                pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).set(**req).write()
            elif action == 'nest.config.dependencies.update':
                pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).update(**req).write()
            elif action == 'nest.config.dependencies.remove':
                pake.config.nest.Dependencies(os.path.join(root, '.pakenest')).remove(**req).write()
            elif action == 'nest.config.files.add':
                pake.config.nest.Files(os.path.join(root, '.pakenest')).add(**req).write()
            else:
                warnings.warn('unknown action: {0}'.format(action))
