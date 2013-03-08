import os
import re
import sys
import random
import collections

os.chdir('..')
sys.path.append('.')

import lib.registry

lib.registry.collect()

print 'Documentation of Included Spells'
print '================================'

for item in sorted(lib.registry.all()):
    spellObj = item['spell']
    name = spellObj.__name__

    # Print out title and underline
    title = '%s -- %s' % (name, spellObj.__doc__)
    print title
    print '-' * len(title)
    print

    # Print out configs
    if spellObj.config:
        print '  * **Required configs**:'
        for config in spellObj.config:
            print '      - ``%s``' % config
    else:
        print '  * **Required configs**: ``None``'

    if item['test']:
        # First collect examples and group them by output. That way we can
        # remove duplicate queries
        examples = collections.defaultdict(list)
        for query, result in item['test'].collectQueries().iteritems():
            examples[result].append(query)
        print '  * **Example usage**:'
        print
        for result, query in examples.iteritems():
            # Choose a random query for this result
            print '    * ``%s``' % random.choice(query)
            print
            print '      * %s' % re.sub('\n+', '\n      * ', result)
            print

    print
