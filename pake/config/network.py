#!/usr/bin/env python3


"""This module contains interfaces to network information/configuration JSON files.
"""


from . import base


class Aliens(base.Config):
    """Interface to aliens.json file.

    Alien dictionary:
        {
            "meta": {},     # metadata about the alien (/meta.json)
            "mirrors": []   # mirrorlist (/mirrors.json)
        }
    """
    name = 'aliens.json'
    default = {}
    content = {}

    def __list__(self):
        return self.all()

    def __contains__(self, url):
        """Checks if nodes.json file contain node of given URL.
        """
        result = False
        for i in self.content:
            if i == url:
                result = True
            else:
                for mirror in self.content[i]:
                    if mirror == url:
                        result = True
                        break
            if result: break
        return result

    def set(self, url, mirrors, meta):
        """Sets node in your list of nodes.
        If a node with given URL already exists it's data is overwritten.
        Part of PAKE fluent API.
        """
        self.content[url] = {'mirrors': mirrors, 'meta': meta}
        return self

    def remove(self, url):
        """Removes alien from the dictionary. Part of PAKE fluent API.
        """
        del self.content[url]
        return self

    def get(self, url):
        """Returns alien dictionary.
        """
        return self.content[url]

    def urls(self):
        """Return list of alien URLs registered in node's network.
        """
        return list(self.content.keys())

    def all(self):
        """Return list of all alien nodes.
        """
        aliens = []
        for u in self.urls():
            # ad -- single "alien dictionary"
            ad = {'url': u}
            d = self.get(u)
            ad['mirrors'] = d['mirrors']
            ad['meta'] = d['meta']
            aliens.append(ad)
        return aliens
