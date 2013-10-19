#!/usr/bin/env python3

"""This module abstracts PAKE packages-index database.
"""

import os
import json
import urllib
import warnings

from pake import config
from pake import shared


def getindex(root):
    """This function will generate and return index of packages that can be found
    in the network.

    :returns: two-tuple (pkg-index, list-of-errors)
    """
    aliens = config.node.Aliens(root)
    index = []
    errors = []
    for url in aliens:
        mirrors = aliens.get(url)['mirrors']
        for m in mirrors:
            print('\t', m)
            try:
                packages = shared.fetchjson('{0}/packages.json'.format(m))
                # if fetch was successful break from loop
                # the assumption is made that mirrors are up-to-date
                break
            except urllib.error.URLError as e:
                errors.append('pake: fail: {0}: while getting packages from {1}'.format(e, m))
                packages = []
            finally:
                pass

        for m in mirrors:
            indexpart = []
            for name in packages:
                pack = {}
                for i in ['meta', 'dependencies', 'versions']:
                    print('trying package: {0}'.format(name))
                    print('\tfrom mirror: {0}'.format(m))
                    resource = '{0}/packages/{1}/{2}.json'.format(m, name, i)
                    try:
                        pack[i] = shared.fetchjson(resource)
                        indexpart.append(pack)
                    except (urllib.error.HTTPError, urllib.error.URLError) as e:
                        errors.append('{0}: {1}'.format(e, resource))
                    finally:
                        pass
            index.extend(indexpart)
    return (index, errors)


def genindex(root):
    """This function will generate index of all packages in the network.
    It is important to call this method before searching or installing any
    package - it's pointless to operate on non-generated (and thus empty)
    index.
    """
    ofstream = open(os.path.join(root, 'db', 'pkgs.json'), 'w')
    ofstream.write(json.dumps(getindex(root)))
    ofstream.close()
