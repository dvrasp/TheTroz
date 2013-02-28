from lib.test import Shaman

queries = [
    (
        "What is the tallest building in the world?",
        "Burj Khalifa (2717 feet)", "tallest_building.xml"
    ), (
        "Where was George Washington born?",
        "Westmoreland County, Virginia", "george_washington_birthplace.xml"
    ), (
        "When is Easter?",
        "Sunday, March 31, 2013", "easter_date.xml"
    ), (
        "How many cups are in a gallon?",
        "16 cups", "cups_in_gallon.xml"
    ), (
        "How much is 15 miles in feet?",
        "79200 feet", "15miles_in_feet.xml"
    ), (
        "15 USD in RMB",
        "yuan93.44  (Chinese yuan)", "15USD_in_RMB.xml"
    )
]


class WolframAlpha(Shaman):

    def setUp(self):
        # Register URLs

        self.config['WolframAlpha']['appID'] = 'test123'

        for question, answer, file in queries:
            self.web.route(
                url='http://api.wolframalpha.com/v2/query',
                get={
                    'input': question,
                    'appid': self.config['WolframAlpha']['appID']
                },
                format='xml',
                file=file
            )

    @Shaman.generate((query[:2] for query in queries))
    def test(self, question, answer):
        self.assertLooksLike(
            self.query(question),
            answer
        )
