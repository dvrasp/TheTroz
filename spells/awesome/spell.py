import lib.spell


class Awesome(lib.spell.BaseSpell):
    """ Raves on how awesome something is """
    weight = 100
    pattern = r"""
        How\s+
        awesome\s+
        (?:is|am)\s+
        ([^?]+)
        \?*
    """
    config = {
        'Personal.FirstName': str,
        'Personal.LastName': str
    }

    def incantation(self, query, config, state):
        first, _, last = query.strip().partition(' ')

        if first.upper() == 'I' and not last:
            first = config['Personal.FirstName']
            last = config['Personal.LastName']

        result = self.fetch(
            'http://api.icndb.com/jokes/random',
            get={
                'firstName': first,
                'lastName': last,
                'exclude': ['explicit']
            },
            format='json'
        )

        if result['type'] == 'success':
            return result['value']['joke'].replace('&quot;', '"'), state
        else:
            return None, state
