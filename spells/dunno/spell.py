import re
import random
import lib.spell


class Dunno(lib.spell.BaseSpell):
    """ When all else fails, make up a random excuse """
    weight = -100
    pattern = r".*"
    reHtml = re.compile('<[^<]+?>')
    reExcuse = re.compile('The cause of the problem is:([^\n]+)')
    apology = [
        'Sorry,', 'Oh dear,', 'I beg you pardon,',
        'Egad!', 'Whoops,', 'Oh snap,',
        'My hunble apologies,', 'Drat!',
        'I would love to help you, but',
    ]


    def incantation(self, query, config, state):
        excuse = self.fetch(
            'http://pages.cs.wisc.edu/~ballard/bofh/bofhserver.pl',
            format='raw'
        )

        return ' '.join((
            random.choice(self.apology),
            self.reExcuse.search(
                self.reHtml.sub('', excuse)
            ).groups()[0]
        )), state
