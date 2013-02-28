import os
import re
import inspect
import datetime
import requests
import StringIO
from xml.etree import ElementTree as ETree


class Pluggable(object):
    _registry = {}

    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            for base in bases:
                cls._registry.setdefault(base.__name__, []).append((
                    cls,
                    os.path.realpath(os.path.split(inspect.getfile(cls))[0])
                ))

    @classmethod
    def registered(cls):
        return cls._registry.get(cls.__name__, [])


class BaseSpell(Pluggable):

    weight = float('-inf')
    pattern = '$a'  # Will never match anything
    blacklist = '$a'  # Ditto
    fetchFormats = {
        'raw': lambda request: request.text,
        'json': lambda request: request.json(),
        'xml': lambda request: ETree.parse(
            StringIO.StringIO(request.text.encode('UTF-8'))
        )._root
    }
    today = datetime.date.today

    def fetch(self, url, post=None, get=None, format='raw'):
        try:
            if post:
                request = requests.post(url, data=post)
            if get:
                request = requests.get(url, params=get)
            else:
                request = requests.get(url)

            request.raise_for_status()

            try:
                return self.fetchFormats[format](request)
            except KeyError:
                raise ValueError('Invalid format: %s' % format)

        except requests.exceptions.HTTPError:
            raise

    def __init__(self):

        self.pattern = re.compile(self.pattern, re.IGNORECASE | re.VERBOSE)
        self.blacklist = re.compile(self.blacklist, re.IGNORECASE | re.VERBOSE)

    def parse(self, query):
        match = self.pattern.match(query)
        if match:
            if self.blacklist.match(query):
                return None, self, float('-inf')
            groups = match.groups()
            if groups:
                return self.weight, self, groups[0]
            else:
                return self.weight, self, query[match.start():match.end()]
        return None, self, float('-inf')

    @classmethod
    def collect(cls):
        for subclass, file in cls.registered():
            if hasattr(subclass, 'incantation'):
                yield subclass, file

    def __str__(self):
        return self.__class__.__name__
