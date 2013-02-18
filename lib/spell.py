import re

class Pluggable(object):
    _registry = {}
    class __metaclass__(type):
        def __init__(cls, name, bases, dict):
            for base in bases:
                cls._registry.setdefault(base.__name__, []).append(cls)

    @classmethod
    def registered(cls):
        return cls._registry.get(cls.__name__, [])

class Spell(Pluggable):

    weight = float('-inf')
    pattern = '$a' # Will never match anything
    blacklist = '$a' # Ditto
    
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
        for subclass in cls.registered():
            if hasattr(subclass, 'incantation'):
                yield subclass

    def __str__(self):
        return self.__class__.__name__
