import os
import re
import mock
import json
import types
import inspect
import requests
import tempfile
import datetime
import itertools
import unittest2
import collections
import spells
import lib.spell


class WebMock(object):

    def __init__(self, root):
        self.root = root
        self.routes = []
        self.mock = mock.patch(
            'lib.spell.BaseSpell.fetch',
            spec=True,
            side_effect=self.mock_fetch
        )

    def route(self, url, file, post=None, get=None, format='raw'):
        with open(os.path.join(self.root, file), 'r') as f:
            request = mock.Mock()
            request.text = f.read().decode('UTF-8')
            request.json = lambda: json.loads(request.text)
            self.routes.append((
                (url, post, get, format),
                lib.spell.BaseSpell.fetchFormats[format](request)
            ))

    def mock_fetch(self, url, post=None, get=None, format='raw'):
        for args, content in self.routes:
            if args == (url, post, get, format):
                return content
        raise Exception(
            'Unknown request: fetch(url=%s, post=%s, get=%s, format=%s)'
            % (url, post, get, format)
        )


class WebCapture(object):
    def __init__(self):
        self._get = requests.get
        self._post = requests.post
        self.patches = (
            mock.patch('requests.get', spec=True, side_effect=self.mock_get),
            mock.patch('requests.post', spec=True, side_effect=self.mock_post)
        )

    def mock_get(self, url, **kwargs):
        print 'url:', url,

        if 'params' in kwargs:
            print 'get:',  kwargs['params'],

        result = self._get(url, **kwargs)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(result.text.encode('UTF-8'))
            print 'Output saved to', f.name

        return result

    def mock_post(self, url, data, **kwargs):
        print 'url:', url,
        print 'data:',  data,

        result = self._post(url, data, **kwargs)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(result.text)
            print 'Output saved to', f.name

        return result

    def __enter__(self):
        for patch in self.patches:
            patch.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for patch in self.patches:
            patch.stop()


class ShamanMetaClass(type):
    def __new__(meta, class_name, bases, class_dict):
        def callback(function, args):
            try:
                string_types = types.StringTypes  # Python2.x
            except AttributeError:
                string_types = str  # Python3

            if isinstance(args, string_types):
                return lambda self: function(self, args)
            else:
                return lambda self: function(self, *args)

        for objName, obj in class_dict.items():
            if hasattr(obj, 'shaman_generate_inputs'):
                for id, input in obj.shaman_generate_inputs:
                    key = '%s_%s' % (obj.__name__, id)
                    class_dict[key] = callback(obj, input)
                del class_dict[objName]
        return type.__new__(meta, class_name, bases, class_dict)


class Shaman(unittest2.TestCase):

    __metaclass__ = ShamanMetaClass

    spell = None

    @classmethod
    def setUpClass(cls):
        root = os.path.realpath(os.path.split(inspect.getfile(cls))[0])
        cls.state = dict()
        cls.config = collections.defaultdict(lambda: collections.defaultdict())
        cls.web = WebMock(os.path.join(root, 'test_data'))
        cls.patches = [cls.web.mock]

        # Search for spell if one is not already provided
        # (a spell that is in the same directory)
        if cls.spell is None:
            for spell in spells.ALL:
                dir = spells.ALL[spell]
                if cls.__name__.lower() == spell.__name__.lower() and root == dir:
                    cls.spell = spell
                    break
            if cls.spell is None:
                raise ValueError(
                    'Unable to detect associated spell for: %s.%s'
                    % (inspect.getfile(cls), cls)
                )

        cls.spell_obj = cls.spell()

    @classmethod
    def generate(cls, *args, **kwargs):
        def wrapper(func):
            inputs = kwargs.items()
            ids = itertools.count(1)
            for arg in args:
                if isinstance(arg, types.GeneratorType):
                    inputs.extend(zip(ids, arg))
                else:
                    inputs.append((ids.next(), arg))

            func.shaman_generate_inputs = inputs
            return func
        return wrapper

    def assertLooksLike(self, first, second, msg=None):
        normalize = lambda string: re.sub(r'\s+', ' ', string).lower().strip()

        if normalize(first) != normalize(second):
            default_msg = (
                '%s\n<[---------- does not look like ----------]>\n%s'
                % (first, second)
            )
            msg = self._formatMessage(msg, default_msg)
            raise self.failureException(msg)

    def query(self, query):
        for patch in self.patches:
            patch.start()

        score, cls, query = self.spell_obj.parse(query)
        result, self.state = self.spell_obj.incantation(
            query, self.config, self.state
        )

        for patch in self.patches:
            patch.stop()

        return result

    def today(self, year, month, day):
        patch = mock.patch(
            'lib.spell.BaseSpell.today',
            lambda self: datetime.date(year, month, day)
        )
        self.patches.append(patch)
