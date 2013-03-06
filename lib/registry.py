import os
import imp
import inspect
import pkgutil
import collections

REGISTRY = collections.defaultdict(lambda: {'spell':None, 'test': None, 'enabled': True})

def collect(root='spells'):
    """
    Recursively find and import all modules under `root`

    :type root: str
    :param root: The directory to start the module searching at
    """

    for loader, name, ispkg in pkgutil.iter_modules([root]):
        collect(os.path.join(root, name))
        fid, pathname, desc = imp.find_module(name, [root])
        if fid:
            imp.load_module(name, fid, pathname, desc)
            fid.close()

def register(**kwargs):
    """
    Register a new spell or test. Classes are automatically grouped
    together by directory (as determined by `get_root`

    :type spell: str
    :param spell: If specified, register a new spell

    :type test: str
    :param test: If specified, register a new test
    """
    for key, cls in kwargs.iteritems():
        root = get_root(cls)
        REGISTRY[root][key] = cls
        REGISTRY[root]['root'] = root

def get_root(cls):
    """
    Get the parent directory of the module that contains class `cls`

    :type cls: class
    :param cls: The class in question

    :rtype: str
    :return: The parent directory path
    """
    return os.path.realpath(os.path.split(inspect.getfile(cls))[0])

def lookup_by_name(**kwargs):
    """
    Return the first group to match the given arguments

    :type spell: str
    :param spell: If specified, search by spell

    :type test: str
    :param test: If specified, search by test

    :rtype: dict
    :return: The group matchinging the given arguments

    The result will be a dictionary with the following keys:
        * `spell`: A class deriving from `lib.spell.BaseSpell`
        * 'test': A class driving from `lib.test.Shaman`
        * 'enabled`: If false, a required configuration is missing.
            Spells are disabled by `lib.config.validate`
    """

    for item in all():
        for key, value in kwargs.iteritems():
            if item[key] and item[key].__name__.lower() == value.lower():
                return item

def all():
    """
    Return all registered spells

    :rtype: list
    :return: A list of dicts (see `lookup_by_name` for
        a description of the structure)
    """
    return REGISTRY.itervalues()

def enabled():
    """
    Return all registered spells in which the 'enabled' value
    is true.

    :rtype: list
    :return: A list of dicts (see `lookup_by_name` for
        a description of the structure)
    """
    return ( value for value in REGISTRY.values() if value['enabled'] )
