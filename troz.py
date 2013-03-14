import os
import sys
import json
import argparse
import textwrap

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest

import lib.registry
import lib.config
import lib.spell
import lib.test
import spells


def ask(query, spell_objs, config, save):
    score = None
    spell = None
    result = None
    canidates = (spell.parse(query) for spell in spell_objs)
    for score, spell, query in sorted(canidates, reverse=True):
            state = save.get(spell.__class__.__name__)
            result, state = spell.incantation(query, config, state)
            if result is None:
                print('Warning: %s failed' % spell)
            else:
                save[spell.__class__.__name__] = state
                break
    return score, spell, result

def get_spells():
    yield 'The following spells are currently installed:'
    for spell in sorted(lib.registry.all(), key=lambda item:item['spell']):
        yield (
            '    * %s%s -- %s'  % (
                not spell['enabled'] and '[needs config] ' or  '',
                spell['spell'].__name__,
                spell['spell'].__doc__
            )
        )

def get_spell_info(spell, width=70):
    spellDict = lib.registry.lookup_by_name(spell=spell)
    spellObj = spellDict['spell']
    if not spellDict['spell']:
        raise RuntimeException

    yield '  * Name: %s' % spellObj.__name__
    yield textwrap.fill(
        '  * Description: %s' % spellObj.__doc__,
        width=width, subsequent_indent=' ' * 4
    )
    if spellObj.config:
        yield '  * Required configs:'
        for config in spellObj.config:
            yield '      - %s' % config
    else:
        yield '  * Required configs: None'

    if spellDict['test']:
        queries = spellDict['test'].collectQueries()
        yield '  * Example usage:'
        for query, result in queries.iteritems():
            yield textwrap.fill(
                '      >>> %s' % query,
                width=width, subsequent_indent=' ' * 10
            )
            yield textwrap.fill(
                '      ... %s' % result,
                width=width, subsequent_indent=' ' * 10
            )

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Your own personal wizard')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query', metavar='"QUERY"', nargs='?', help="Your query to troz, in quotes")
    group.add_argument('--spell-list', dest='doList', action='store_const', const=True, default=False, help='List all spells currently installed')
    group.add_argument('--spell-info', dest='doInfo', metavar='SPELL', help='Get detailed information a specific spell')
    group.add_argument('--test', action='store_const', const=True, help='Run test suite')
    parser.add_argument('--capture', action='store_const', const=True, help='Output debugging info and save fetched queries to disk')

    args = parser.parse_args()
    lib.registry.collect()

    if args.doList:
        parser.exit('\n'.join(get_spells()))
    elif args.doInfo:
        parser.exit('\n'.join(get_spell_info(args.doInfo)))
    elif args.test:
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        suite.addTests(
            loader.loadTestsFromTestCase(item['test'])
            for item in lib.registry.all() if item['test']
        )
        testRunner = unittest.runner.TextTestRunner(verbosity=2)
        result = testRunner.run(suite)
        parser.exit(len(result.errors))
    elif not args.query:
        parser.print_help()
        parser.exit()

    config = lib.config.load('settings.conf')

    spell_objs = [item['spell']() for item in lib.registry.enabled()]

    if os.path.exists('save.db'):
        with open('save.db') as f:
            save = json.load(f)
    else:
        save = {}

    if args.capture:
        with lib.test.WebCapture():
            print(ask(args.query, spell_objs, config, save)[-1])
    else:
        print(ask(args.query, spell_objs, config, save)[-1])

    with open('save.db', 'w') as f:
        json.dump(save, f)
