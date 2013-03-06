import lib.spell
from dateutil import relativedelta as rdelta


class Templates(object):
    current = "Curently, it's %s and %s. "
    forecast_parts = (
        "By the %(period)s, the weather will turn %(description)s. ",
        "The %(period)s will be %(description)s. ",
        "It looks like the %(period)s of %(date)s will be %(description)s. ",
    )  # Backwards so we can pop()


class Forecast(object):

    # Definitions are based on http://www.wrh.noaa.gov/mtr/glossary.php
    terms = {
        'cloud': [
            (12, 'CLEAR'),
            (24, 'MOSTLY CLEAR'),
            (60, 'PARTLY CLEAR'),
            (84, 'MOSTLY CLOUDY'),
            (float('inf'), 'CLOUDY'),
        ],
        'wind': [
            (00.44, ''),
            (02.24, 'LIGHTLY WINDY'),
            (06.71, 'SLIGHTLY WINDY'),
            (11.18, 'BREEZY'),
            (15.65, 'WINDY'),
            (17.88, 'VERY WINDY'),
            (float('inf'), 'EMTREMELY WINDY'),
        ],
        'chance': [
            (20, 'slight chance of'),
            (40, 'chance of'),
            (80, 'likely chance of'),
            (float('inf'), ''),
        ],
        'intensity': [
            (0.76, 'VERY LIGHTLY'),
            (7.62, 'LIGHTLY'),
            (22.9, 'MODERATELY'),
            (float('inf'), 'HEAVILY'),
        ],
    }

    def __new__(self, data):
        # Data must be of the following format:
        # [morning1, morning2, afternoon1, afternoon2, evening1, evening2]
        # If there is no data for a given time slot,
        #   the value for that position should be None
        forecast = [self.humanTerms(item) for item in data]
        return (
            ('morning', self.stringify(*forecast[0:2])),
            ('afternoon', self.stringify(*forecast[2:4])),
            ('evening', self.stringify(*forecast[4:]))
        )

    @classmethod
    def humanTerms(cls, item):
        if item is None:
            return (None, None)

        terms = cls.terms

        description = []
        temperature = [
            int(item['main']['temp_min']),
            int(item['main']['temp_max']),
            int(item['main']['temp'])
        ]

        clouds = item['clouds']['all']
        for num, string in terms['cloud']:
            if clouds <= num:
                if string:
                    description.append(string)
                break

        wind = item['wind']['speed']
        for num, string in terms['wind']:
            if wind <= num:
                if string:
                    description.append(string)
                break

        if 'snow' in item:
            snow = item['snow']['3h']
            for num, string in terms['intensity']:
                if snow <= num:
                    if string:
                        description.append(string + ' snowing')
                    break

        if 'rain' in item:
            rain = item['rain']['3h']
            for num, string in terms['intensity']:
                if rain <= num:
                    if string:
                        description.append(string + ' raining')
                    break

        # Unfortunately, openWeatherMap doesn't
        #   have PoP (probability of percipitation) data
        return temperature, description

    @staticmethod
    def stringify(weather1, weather2):
        # Possible conditions:
        #   (a): The two conditions are the same
        #   (b): The two conditions are different
        #   (c): Only one condition exists

        temperature1, description1 = weather1
        temperature2, description2 = weather2

        if not (temperature1 and temperature2):
            if temperature1:
                temperature2 = temperature1
                description2 = description1
            elif temperature2:
                temperature1 = temperature2
                description1 = description2
            else:
                return ''

        low = temperature1[0]
        high = temperature2[1]

        def _stringify(elements):
            if len(elements) == 1:
                return ', '.join(elements)
            else:
                return '%s and %s' % (', '.join(elements[:-1]), elements[-1])

        if description1 == description2:
            return (
                "%s (high %s/low %s)"
                % (_stringify(description1), high, low)
            )
        else:
            # Remove items from description2 that are in description1
            description2 = [
                item
                for item in description2
                if item not in description1
            ]

            return '%s, becoming %s later on (high %s/low %s)' % (
                _stringify(description1), _stringify(description2), high, low
            )


class OpenWeatherMap(lib.spell.BaseSpell):
    """ Gets the current weather conditions and forecast """
    weight = 100
    pattern = r"""
        # What is the current weather?
        # What is the current forecast?
        # What will today's weather be like?
        # What will saturday's weather be like?
        # What is the forecast for next Tuesday?
        # What is next Friday's forecast for Dallas, Texas?
        # What is the weather like in Dallas, Texas?
        (?:
            What
            \s+(?:is|will)
            (?:\s+(?:the|be))?
            (
                \s+.+
                \s+(?:weather|forecast)
                [^?]*
            )
            \?*
        )
    """

    offsetKeys = set([
        'current', 'today', 'tomorrow', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'weekend'
    ])

    offsets = {
        'current': [rdelta.relativedelta(days=0)],
        'today': [rdelta.relativedelta(days=0)],
        'tomorrow': [rdelta.relativedelta(days=1)],
        'monday': [rdelta.relativedelta(weekday=rdelta.MO)],
        'tuesday': [rdelta.relativedelta(weekday=rdelta.TU)],
        'wednesday': [rdelta.relativedelta(weekday=rdelta.WE)],
        'thursday': [rdelta.relativedelta(weekday=rdelta.TH)],
        'friday': [rdelta.relativedelta(weekday=rdelta.FR)],
        'saturday': [rdelta.relativedelta(weekday=rdelta.SA)],
        'sunday': [rdelta.relativedelta(weekday=rdelta.SU)],
        'weekend': [
            rdelta.relativedelta(weekday=rdelta.SA),
            rdelta.relativedelta(weekday=rdelta.SU)
        ],
    }

    hours = [
        ' 05:00:00',  # morning 1
        ' 08:00:00',  # morning 2
        ' 11:00:00',  # afternoon 1
        ' 14:00:00',  # afternoon 2
        ' 17:00:00',  # evening 1
        ' 20:00:00',  # evening 2
    ]

    config = {
        'Weather.Location': str,
        'Weather.Units': [str, 'metric', 'imperial']
    }

    def incantation(self, query, config, state):
        result = ['']

        if state is None:
            state = {}

        today = self.today()
        query_words = [word for word in query.split(' ') if word]

        if 'next' in query_words:
            # There's no way we'll have enough data
            return None, state

        if 'for' in query_words:
            index = query_words.index('for')
            query_loc = ' '.join(query_words[index+1:])
            del query_words[index:]
        elif 'in' in query_words:
            index = query_words.index('in')
            query_loc = ' '.join(query_words[index+1:])
            del query_words[index:]
        else:
            query_loc = config['Weather.Location']

        query_words = set((word.rstrip("'s").lower() for word in query_words))
        query_words.intersection_update(self.offsetKeys)
        try:
            weekday = tuple(query_words)[0]
            offsets = self.offsets[weekday]
        except (KeyError, IndexError):
            # Just give the current weather
            weekday = 'current'
            offsets = self.offsets[weekday]
        try:
            location_id = state[query_loc]
        except KeyError:
            data = self.fetch(
                'http://api.openweathermap.org/data/2.1/find/name',
                get={'q': query_loc},
                format='json'
            )
            try:
                location_id = state[query_loc] = data['list'][0]['id']
            except KeyError:
                return None, state

        if weekday in ('current', 'today'):
            url = (
                'http://api.openweathermap.org/data/2.1/weather/city/%s'
                % location_id
            )

            data = self.fetch(
                url,
                get={'units': config['Weather.Units']},
                format='json'
            )
            temperature, description = Forecast.humanTerms(data)
            elements = [str(temperature[2])] + description
            result.append(
                Templates.current
                % (', '.join(elements[:-1]), elements[-1])
            )
            weekday = 'today'

        # Finally, let's get the data!
        url = (
            'http://api.openweathermap.org/data/2.2/forecast/city/%s'
            % location_id
        )

        data = self.fetch(
            url,
            get={'units': config['Weather.Units']},
            format='json'
        )

        for offset in offsets:
            if len(result) > 1:
                result.append("\n\n")

            date_obj = today + offset
            date_string = date_obj.strftime('%Y-%m-%d')
            dates = [date_string + hour for hour in self.hours]
            forecast_dates = dict(((date, None) for date in dates))
            forecast_parts = list(Templates.forecast_parts)

            for item in data['list']:
                if item['dt_txt'] in forecast_dates:
                    forecast_dates[item['dt_txt']] = item

            values = {
                'date': date_obj.strftime('%a, %b %e')
            }

            forecast = (
                Forecast((
                    forecast_dates[x] for x in sorted(forecast_dates)
                ))
            )

            for values['period'], values['description'] in forecast:
                if values['description']:
                    result.append(forecast_parts.pop() % values)

        return "".join(result), state
