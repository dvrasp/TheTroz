import os
import imp
import pkgutil
import lib.spell

def collect_spells(root='spells'):
    for loader, name, ispkg in pkgutil.iter_modules([root]):
        collect_spells(os.path.join(root, name))
        fid, pathname, desc = imp.find_module(name, [root])
        imp.load_module(name, fid, pathname, desc)
        if fid:
            fid.close()

collect_spells()

ALL = set(lib.spell.Spell.collect())
