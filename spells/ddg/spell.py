import lib.spell


class DDG(lib.spell.BaseSpell):
    weight = 100
    pattern = r"""
        # 1 + 1
        (?:
            \d\s+[^\s]+\s+\d
        )|

        # What are cookies? Who was George Washington?
        (?:
            (?:who|what)
            \s+(?:is|are|was)
            \s+(?:the|a|an)?
            ([^?]*)
            \?*
        )
    """

    def incantation(self, query, config, state):
        result = self.fetch(
            'http://api.duckduckgo.com',
            get={
                'q': query,
                'format': 'json',
                'no_redirect': 1,
                'no_html': 1,
                'skip_disambig': 1
            },
            format='json'
        )
        value = (
            result.get('Answer', None) or
            result.get('Abstract', None) or
            result.get('Definition', None) or
            None
        )
        return value, state
