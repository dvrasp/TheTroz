from lib.test import Shaman


class DDG(Shaman):

    def setUp(self):
        # Register URLs
        self.web.route(
            url='http://api.duckduckgo.com',
            get={
                'q': 'George Washington',
                'no_html': 1,
                'no_redirect': 1,
                'skip_disambig': 1,
                'format': 'json'
            },
            format='json',
            file='george_washington.dat'
        )

        self.web.route(
            url='http://api.duckduckgo.com',
            get={
                'q': 'cookies',
                'no_html': 1,
                'no_redirect': 1,
                'skip_disambig': 1,
                'format': 'json'
            },
            format='json',
            file='cookies.dat'
        )

        self.web.route(
            url='http://api.duckduckgo.com',
            get={
                'q': '13 + 14',
                'no_html': 1,
                'no_redirect': 1,
                'skip_disambig': 1,
                'format': 'json'
            },
            format='json',
            file='13_plus_14.dat'
        )

    def test_george_washington(self):
        result = self.query("Who is George Washington?")
        expected = """
            George Washington was one of the Founding
            Fathers of the United States, serving as
            the commander-in-chief of the Continental Army
            during the American Revolutionary War.
        """
        self.assertLooksLike(result, expected)

    def test_cookies(self):
        result = self.query("What are cookies?")
        expected = """
            A small, usually flat and crisp cake made from sweetened dough.
        """
        self.assertLooksLike(result, expected)

    def test_13_plus_14(self):
        # Run a test, check the result and state
        result = self.query("What is 13 + 14?")
        expected = "13 + 14 = 27"
        self.assertLooksLike(result, expected)
