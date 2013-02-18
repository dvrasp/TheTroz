import sys
import yaml
import configobj

import lib.spell
import spells

def ask(query, spellObjs, config, state):
    score = None
    spell = None
    result = None
    for score, spell, query in sorted((spell.parse(query) for spell in spellObjs), reverse=True):
            result, state = spell.incantation(query, config, state)
            if result is None:
                print 'Warning: %s failed' % spell
            else:
                break
    return score, spell, result

if __name__ == "__main__":

    config = configobj.ConfigObj('settings.conf')
    spellObjs = [ spell() for spell in spells.ALL ]
    query = ' '.join(sys.argv[1:])

    if not query or '-help' in query or '-?' in query:
        print >> sys.stderr, (
            "Usage: %s [query]"
            "   Example Queries:"
            '       "What is the weather going to be like tomorrow for 21520?"'
            '       "How many cups are in a quart?"'
            '       "What is 12 + 421?"'
        )

    print '[%s:%s] The Wizard of Troz Says: "%s"' % ask(query, spellObjs, config, None)
