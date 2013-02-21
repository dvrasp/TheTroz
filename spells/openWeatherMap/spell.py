import itertools
import lib.web
from datetime import date
from dateutil import relativedelta as rdelta

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
            (02.24, 'a LIGHT WIND'),
            (06.71, 'a SLIGHT WIND'),
            (11.18, 'BREEZY'),
            (15.65, 'WINDY'),
            (17.88, 'VERY WINDY'),
            (float('inf'), 'EXTREMELY STRONG WINDS'),
        ],
        'chance': [
            (20, 'slight chance of'),
            (40, 'chance of'),
            (80, 'likely chance of'),
            (float('inf'), ''),
        ],
        'intensity': [
            (0.76, 'VERY LIGHT'),
            (7.62, 'LIGHT'),
            (22.9, 'MODERATE'),
            (float('inf'), 'HEAVY'),
        ],
    }

    def __init__(self, data):
        # Data must be of the following format:
        # [morning1, morning2, afternoon1, afternoon2, evening1, evening2]
        # If there is no data for a given time slot the value for that position should be None
        humanData = [self.humanTerms(item) for item in data]
        self.string = "\n".join((
            self.stringify('Morning', *humanData[0:2]),
            self.stringify('Afternoon', *humanData[2:4]),
            self.stringify('Evening', *humanData[4:]),
        ))

    def __str__(self):
        return self.string

    def __unicode__(self):
        return self.string

    @classmethod
    def humanTerms(cls, item):
        if item is None:
            return (None, None)

        data = {}
        terms = cls.terms

        description = []
        temperature = [int(item['main']['temp_min']), int(item['main']['temp_max']), int(item['main']['temp'])]

        clouds = item['clouds']['all']
        for num, string in terms['cloud']:
            if clouds <= num:
                description.append(string)
                break

        wind = item['wind']['speed']
        for num, string in terms['wind']:
            if wind <= num:
                description.append(string)
                break

        if 'snow' in item:
            snow = item['snow']['3h']
            for num, string in terms['intensity']:
                if snow <= num:
                    description.append(string + ' snow')
                    break

        if 'rain' in item:
            rain = item['rain']['3h']
            for num, string in terms['intensity']:
                if rain <= num:
                    description.append(string + ' rain')
                    break

        # Unfortunately, openWeatherMap doesn't have PoP (probability of percipitation) data
        return temperature, description

    def stringify(self, name, weather1, weather2):
        # Possible conditions:
        #   (a): The two conditions are the same
        #       => mostly cloudy, starting at mid 60's and going up to high 80's
        #   (b): The two conditions are different
        #       => a chance of scattered showers, becoming snow later on. Low of 23 and high of 35
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
            return '%s: high of %s, low of %s; %s.' % (name, high, low, _stringify(description1))
        else:
            # Remove items from description2 that are in description1
            description2 = [item for item in description2 if item not in description1]
            return '%s: high of %s, low of %s; %s becoming %s later on.' % (name, high, low, _stringify(description1), _stringify(description2))

class OpenWeatherMap(lib.spell.Spell):
    weight = 100
    pattern = r"""
        # What is the current weather?
        # What is the current forecast?
        # What will today's weather be like?
        # What will saturday's weather be like?
        # What is the forecast for next Tuesday?
        # What is next Friday's forecast for Changping, Beijing?
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

    offsetKeys = set(['current', 'today', 'tomorrow', 'monday', 'tuesday',
                      'wednesday', 'thursday', 'friday', 'saturday', 'sunday','weekend'])

    offsets = {
        'current': [ rdelta.relativedelta(days=0) ],
        'today': [ rdelta.relativedelta(days=0) ],
        'tomorrow': [ rdelta.relativedelta(days=1) ],
        'monday': [ rdelta.relativedelta(weekday=rdelta.MO) ],
        'tuesday': [ rdelta.relativedelta(weekday=rdelta.TU) ],
        'wednesday': [ rdelta.relativedelta(weekday=rdelta.WE) ],
        'thursday': [ rdelta.relativedelta(weekday=rdelta.TH) ],
        'friday': [ rdelta.relativedelta(weekday=rdelta.FR) ],
        'saturday': [ rdelta.relativedelta(weekday=rdelta.SA) ],
        'sunday': [ rdelta.relativedelta(weekday=rdelta.SU) ],
        'weekend': [ rdelta.relativedelta(weekday=rdelta.SA), rdelta.relativedelta(weekday=rdelta.SU) ],
    }

    hours = [
        ' 05:00:00', # morning 1
        ' 08:00:00', # morning 2
        ' 11:00:00', # afternoon 1
        ' 14:00:00', # afternoon 2
        ' 17:00:00', # evening 1
        ' 20:00:00', # evening 2
    ]

    def incantation(self, query, config, state):
        result = ['']

        if state is None:
            state = {}

        today = date.today()
        queryWords = [word for word in query.split(' ') if word]

        print queryWords

        if 'next' in queryWords:
            # There's no way we'll have enough data
            return None, state

        if 'for' in queryWords:
            index = queryWords.index('for')
            queryLoc = ' '.join(queryWords[index+1:])
            del queryWords[index:]
        else:
            queryLoc = config['Weather']['location']

        queryWords = set((word.rstrip("'s").lower() for word in queryWords))
        queryWords.intersection_update(self.offsetKeys)
        try:
            weekday = tuple(queryWords)[0]
            offsets = self.offsets[weekday]
        except (KeyError, IndexError):
            # No idea what the user is asking for
            return None, state

        try:
            locationID = state[queryLoc]
        except KeyError:
            data = lib.web.fetch('http://api.openweathermap.org/data/2.1/find/name?q=' + queryLoc, format='json')
            try:
                locationID = state[queryLoc] = data['list'][0]['id']
            except KeyError:
                return None, state

        if weekday in ('current','today'):
            data = lib.web.fetch(
                'http://api.openweathermap.org/data/2.1/weather/city/' + `locationID`,
                get = {'units': config['Weather']['units']},
                format = 'json'
            )
            temperature, description = Forecast.humanTerms(data)
            elements = [`temperature[2]`] + description
            result.append("Currently it's %s and %s" % (', '.join(elements[:-1]), elements[-1]))

        # Finally, let's get the data!
        data = lib.web.fetch(
            'http://api.openweathermap.org/data/2.2/forecast/city/' + `locationID`,
            get = {'units': config['Weather']['units']},
            format = 'json'
        )

        for offset in offsets:
            dateObj = today + offset
            dateStr = dateObj.strftime('%Y-%m-%d')
            dates = [ dateStr + hour for hour in self.hours ]
            forecastDates = dict(((date, None) for date in dates))
            result.append('== Forecast for %s: ==' % dateObj.strftime('%a, %b %e'))

            for item in data['list']:
                if item['dt_txt'] in forecastDates:
                    forecastDates[item['dt_txt']] = item

            forecast = Forecast((forecastDates[x] for x in sorted(forecastDates)))
            result.append(str(forecast))

        return "\n".join(result), state
