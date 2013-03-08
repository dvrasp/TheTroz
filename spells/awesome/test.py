from lib.test import Shaman


class Awesome(Shaman):

    def setUp(self):
        # Register URLs
        self.web.route(
            url='http://api.icndb.com/jokes/random',
            get={
                'firstName': 'Peter',
                'lastName': 'Naudus',
                'exclude': ['explicit']
            },
            format='json',
            file='peter_naudus.json'
        )

        self.web.route(
            url='http://api.icndb.com/jokes/random',
            get={
                'firstName': 'Chuck',
                'lastName': 'Norris',
                'exclude': ['explicit']
            },
            format='json',
            file='chuck_norris.json'
        )

        self.config['Personal.FirstName'] = 'Peter'
        self.config['Personal.LastName'] = 'Naudus'

    @Shaman.generate('How awesome am I?', 'How awesome is Peter Naudus?')
    def test_peter_naudus(self, question):
        result = self.query(question)
        expected = """
            Peter Naudus invented black. In fact, he invented
            the entire spectrum of visible light. Except pink.
            Tom Cruise invented pink.
        """
        self.assertLooksLike(result, expected)

    def test_chuck_norris(self):
        result = self.query("How awesome is Chuck Norris?")
        expected = """
            The Manhattan Project was not intended to create
            nuclear weapons, it was meant to recreate the
            destructive power in a Chuck Norris Roundhouse
            Kick. They didn't even come close.
        """
        self.assertLooksLike(result, expected)
