import os
import sys
import yaml
import configobj

try:
    import cPickle as pickle
except ImportError:
    import pickle

import lib.spell
import lib.test
import lib.web
import spells

def ask(query, spellObjs, config, save):
    score = None
    spell = None
    result = None
    for score, spell, query in sorted((spell.parse(query) for spell in spellObjs), reverse=True):
            state = save.get(spell.__class__.__name__)
            result, state = spell.incantation(query, config, state)
            if result is None:
                print 'Warning: %s failed' % spell
            else:
                save[spell.__class__.__name__] = state
                break
    return score, spell, result

if __name__ == "__main__":

    config = configobj.ConfigObj('settings.conf')
    spellObjs = [ spell() for spell in spells.ALL ]
    query = ' '.join(sys.argv[1:])

    if not query or '-help' in query or '-?' in query:
        print >> sys.stderr, (
            "Usage: %s [query]\n"
            "   Example Queries:\n"
            '       "What is the weather going to be like tomorrow for 21520?"\n'
            '       "How many cups are in a quart?"\n'
            '       "What is 12 + 421?"\n'
        )
        sys.exit()

    if os.path.exists('save.db'):
        with open('save.db') as f:
            save = pickle.load(f)
    else:
        save = {}

    with lib.test.WebCapture():
        print '[%s:%s] The Wizard of Troz Says: "%s"' % ask(query, spellObjs, config, save)

    with open('save.db', 'w') as f:
        pickle.dump(save, f)
