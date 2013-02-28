import re
import os
import imp
import pkgutil
import lib.spell


classSpellRE = re.compile(r'class\s+[^\(]+\(.*BaseSpell\s*\)\s*:')


def collect_spells(root='spells'):
    for loader, name, ispkg in pkgutil.iter_modules([root]):
        collect_spells(os.path.join(root, name))
        fid, pathname, desc = imp.find_module(name, [root])
        if fid:
            if any((classSpellRE.match(line) for line in fid)):
                fid.seek(0)
                imp.load_module(name, fid, pathname, desc)
            fid.close()

collect_spells()

ALL = dict(lib.spell.BaseSpell.collect())
