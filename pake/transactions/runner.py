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
    def __init__(self, path, requests):
        """:param path: directory that transactions are run in (can be overridden by setting 'path' for individual requests)
        :param requests: list of requests
        """
        self._path = path
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
            if 'path' in req: path = req['path']
            else: path = self._path
            if action == 'node.manager.init':
                pake.node.manager.makedirs(path)
                pake.node.manager.makeconfig(path)
            elif action == 'node.manager.remove':
                pake.node.manager.remove(req['path'])
            elif action == 'node.config.meta.set':
                pake.config.node.Meta(os.path.join(path, '.pakenode')).set(req['key'], req['value']).write()
            elif action == 'node.config.meta.remove':
                pake.config.node.Meta(os.path.join(path, '.pakenode')).remove(req['key']).write()
            elif action == 'node.config.mirrors.set':
                pake.config.node.Pushers(os.path.join(path, '.pakenode')).set(url=req['url'], host=req['host'], cwd=req['cwd']).write()
            elif action == 'node.config.mirrors.remove':
                pake.config.node.Pushers(os.path.join(path, '.pakenode')).remove(url=req['url']).write()
            elif action == 'node.config.aliens.set':
                pake.config.node.Aliens(os.path.join(path, '.pakenode')).set(url=req['url'], mirrors=req['mirrors'], meta=req['meta']).write()
            elif action == 'node.config.aliens.remove':
                pake.config.node.Aliens(os.path.join(path, '.pakenode')).remove(url=req['url']).write()
            else:
                warnings.warn('unknown action: {0}'.format(action))
