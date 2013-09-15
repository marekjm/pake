import os
import shutil

from pake import config


def makedirs(root):
    """Creates new PAKE repository.

    :param root: root of the repository
    :type root: str
    """
    subdirectories = ['releases']
    os.mkdir(root)
    for name in subdirectories: os.mkdir(os.path.join(root, name))


def makeconfig(root):
    """Initializes empty PAKE repository.

    :param root: root for the repository
    :type root: str
    """
    config.repository.Meta(root).reset()
    config.repository.Dependencies(root).reset()
    config.repository.Files(root).reset()


def remove(root):
    """Removes repository.
    """
    shutil.rmtree(root)
