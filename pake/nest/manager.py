import os
import shutil

from pake import config


def makedirs(root):
    """Creates new PAKE nest.

    :param root: root of the nest
    :type root: str
    """
    subdirectories = ['releases']
    os.mkdir(root)
    for name in subdirectories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Initializes empty PAKE nest.

    :param root: root for the nest
    :type root: str
    """
    config.nest.Versions(root).reset()
    config.nest.Dependencies(root).reset()
    config.nest.Files(root).reset()
    config.nest.Meta(root).reset()


def remove(root):
    """Removes nest.
    """
    shutil.rmtree(root)
