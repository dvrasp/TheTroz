from lib.test import Shaman


class OpenWeatherMap(Shaman):

    def setUp(self):
        # Set the time
        self.today(2013, 2, 22)

        # Set up config
        self.config['Weather']['location'] = 'Accident, Maryland, USA'
        self.config['Weather']['units'] = 'imperial'

        # Register URLs
        self.web.route(
            url='http://api.openweathermap.org/data/2.1/find/name',
            get={'q': self.config['Weather']['location']},
            format='json',
            file='find_accident_maryland.json'
        )

        self.web.route(
            url='http://api.openweathermap.org/data/2.1/find/name',
            get={'q': 'Dallas, Texas'},
            format='json',
            file='find_accident_maryland.json'
        )

        self.web.route(
            url='http://api.openweathermap.org/data/2.1/weather/city/4363282',
            get={'units': self.config['Weather']['units']},
            format='json',
            file='weather_accident_maryland.json'
        )

        self.web.route(
            url='http://api.openweathermap.org/data/2.2/forecast/city/4363282',
            get={'units': self.config['Weather']['units']},
            format='json',
            file='forecast_accident_maryland.json'
        )

    @Shaman.generate(
        "What is today's weather",
        "What is the current weather",
        "What is today's forecast?",
        "What will today's weather be like?"
    )
    def test_today(self, query):
        # Run a test, check the output and state
        output = """
                Curently, it's 23, CLOUDY and WINDY.
                It looks like the evening of Fri, Feb 22 will be
                CLOUDY, BREEZY and LIGHT rain,
                becoming VERY LIGHT rain later on (high 33/low 23).
            """
        self.assertLooksLike(self.query(query), output)
        self.assertEqual(self.state['Accident, Maryland, USA'], 4363282)

    @Shaman.generate(
        "What is tomorrow's weather",
        "What is tomorrow's forecast?",
        "What will tomorrow's weather be like?"
    )
    def test_tomorrow(self, query):
        # Run a test, check the output and state
        output = """
                It looks like the morning of Sat, Feb 23 will be
                CLOUDY and BREEZY, becoming SLIGHTLY WINDY and
                VERY LIGHT rain later on (high 29/low 22).
                The afternoon will be CLOUDY, SLIGHTLY WINDY
                and LIGHT rain (high 35/low 27).
                By the evening, the weather will turn CLOUDY,
                SLIGHTLY WINDY and LIGHT rain, becoming
                VERY LIGHT rain later on (high 40/low 32).
            """
        self.assertLooksLike(self.query(query), output)

    @Shaman.generate(
        "What is the weekend's weather",
        "What is the weekend's forecast?",
        "What will the weekend's weather be like?"
    )
    def test_weekend(self, query):
        # Run a test, check the output and state
        output = """
                It looks like the morning of Sat, Feb 23 will be
                CLOUDY and BREEZY, becoming SLIGHTLY WINDY and
                VERY LIGHT rain later on (high 29/low 22).
                The afternoon will be CLOUDY,
                SLIGHTLY WINDY and LIGHT rain (high 35/low 27).
                By the evening, the weather will turn
                CLOUDY, SLIGHTLY WINDY and LIGHT rain,
                becoming VERY LIGHT rain later on (high 40/low 32).

                It looks like the morning of Sun, Feb 24
                will be CLOUDY, SLIGHTLY WINDY and VERY LIGHT snow,
                becoming BREEZY later on (high 31/low 29).
                The afternoon will be CLOUDY, BREEZY and VERY LIGHT snow,
                becoming WINDY later on (high 28/low 24).
                By the evening, the weather will turn CLOUDY,
                WINDY and VERY LIGHT snow,
                becoming CLEAR later on (high 35/low 26).
            """
        self.assertLooksLike(self.query(query), output)

    @Shaman.generate(
        "What is Thursday's weather?",
        "What is Thursday's forecast?",
        "What will Thursday's weather be like?"
    )
    def test_thursday(self, query):
        # Run a test, check the output and state
        output = """
                It looks like the morning of Thu, Feb 28 will be CLOUDY,
                WINDY and LIGHT snow, becoming VERY LIGHT
                snow later on (high 26/low 26).
                The afternoon will be CLOUDY,
                WINDY and LIGHT snow (high 27/low 24).
                By the evening, the weather will turn CLOUDY,
                VERY WINDY and LIGHT snow,
                becoming WINDY later on (high 30/low 24).
            """
        self.assertLooksLike(self.query(query), output)

    @Shaman.generate(
        "What is Thursday's weather for Dallas, Texas?",
        "What is Thursday's forecast for Dallas, Texas?",
        "What will Thursday's weather be like in Dallas, Texas?"
    )
    def test_dallas(self, query):
        # Run a test, check the output and state
        output = """
                It looks like the morning of Thu,
                Feb 28 will be CLOUDY, WINDY and LIGHT snow,
                becoming VERY LIGHT snow later on (high 26/low 26).
                The afternoon will be CLOUDY,
                WINDY and LIGHT snow (high 27/low 24).
                By the evening, the weather will turn CLOUDY,
                VERY WINDY and LIGHT snow,
                becoming WINDY later on (high 30/low 24).
            """
        self.assertLooksLike(self.query(query), output)
        self.assertEqual(self.state['Dallas, Texas'], 4363282)
