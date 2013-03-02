import time
import lib.spell


class WolframAlpha(lib.spell.BaseSpell):
    weight = 75
    pattern = r"""
        # 1 + 1
        (?:\d\s+[^\s]+\s+\d)|

        # What is the tallest building in the world?
        # Where was George Washington born? When is Christmas?
        (?:
            (?:who|what|when|where|why)
            \s+(?:is|are|was)
            \s+(?:the|a|an)?
            [^?]*
            \?*
        )|

        # How many cups are in a gallon? How much is 15 miles in feet?
        (?:
            (?:how)
            \s+(?:many|much)
            \s+[^?]*
            \?*
        )|

        # 15 USD in RMB
        (?:
            (?:\d+\s+|\d+\S+\s+)
            \S+
            \s+in
            \s+[^\s+?]+
            \?*
        )
    """
    blacklist = "\s+(?:you|you're|your)\s+"
    config = {
        'WolframAlpha.AppID': str
    }

    def incantation(self, query, config, state):
        # For some reason, sometimes W|A returns blank data.
        # We'll try 3 times to get the data
        inf = float('inf')
        result_relevance = -inf
        result_value = None
        for _ in range(3):
            data = self.fetch(
                'http://api.wolframalpha.com/v2/query',
                get={
                    'input': query,
                    'appid': config['WolframAlpha.AppID']
                },
                format='xml'
            )

            if data.attrib['success'] == 'true':
                if data.attrib['numpods'] == '0':
                    self.log.warning('Strange data, trying again ...')
                    time.sleep(1)
                    continue

                for pod in data.findall('pod'):
                    # Search through the pods looking for the best one
                    attrib = pod.attrib
                    if attrib.get('primary') == 'true':
                        relevance = attrib.get('id') == 'Result' and 100 or 90
                    elif attrib.get('scanner') == 'Data' and 'NotableFacts' in attrib.get('id'):
                        relevance = 80
                    else:
                        relevance = -inf

                    if relevance > result_relevance:
                        result_relevance = relevance
                        result_value = pod.findall('subpod')[0].find('plaintext').text

            return result_value, state
