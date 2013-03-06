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
import lib
import lib.spell
import lib.registry


class WebMock(object):
    """
        :type root: str
        :param root: The root directory that contains the data files that
            will be used in the mock
    """

    def __init__(self, root):
        self.root = root
        self.routes = []
        self.mock = mock.patch(
            'lib.spell.BaseSpell.fetch',
            spec=True,
            side_effect=self.mock_fetch
        )

    def route(self, url, file, post=None, get=None, format='raw'):
        """
            :type url: str
            :param url: The base URL to intercept. Do not include the query string

            :type file: str
            :param file: The file name (in ``self.root``) that contains the response
                data corresponding to the request

            :type post: dict or None
            :param post: If set, will only intercept URLs which have post
                data matching ``post``

            :type post: dict or None
            :param post: If set, will only intercept URLs which have get
                data matching ``post``

            :type format: str
            :param format: Only requests asking for the same format will be
                handled
        """
        with open(os.path.join(self.root, file), 'r') as f:
            request = mock.Mock()
            request.text = f.read().decode('UTF-8')
            request.json = lambda: json.loads(request.text)
            self.routes.append((
                (url, post, get, format),
                lib.spell.BaseSpell.fetchFormats[format](request)
            ))

    def mock_fetch(self, url, post=None, get=None, format='raw'):
        """
        This function replaces ``lib.spell.BaseSpell.fetch`` when the mock
        is active.

        :raises:Exception: Any request that does not match one predefined with ``route()``
            will result in an ``Exception`` being thrown.
        """

        for args, content in self.routes:
            if args == (url, post, get, format):
                return content
        raise Exception(
            'Unknown request: fetch(url=%s, post=%s, get=%s, format=%s)'
            % (url, post, get, format)
        )


class WebCapture(object):
    """
    This is a proxy class that intercepts web requests and then
    prints information to the screen and also saves the result
    to a temporary file.

    This is used to quickly build up test cases in a
    pseudo record/playback manner.
    """

    def __init__(self):
        self._get = requests.get
        self._post = requests.post
        self.patches = (
            mock.patch('requests.get', spec=True, side_effect=self.mock_get),
            mock.patch('requests.post', spec=True, side_effect=self.mock_post)
        )

    def mock_get(self, url, **kwargs):
        """
        This replaces ``requests.get``. It prints out the ``kwargs`` that
        is used to build the query string, passes the request along to
        the original ``get(...)`` function and then saves the result to a file

        :type url: str
        :param url: The URL of the resource being requested

        :type kwargs: dict
        :param kwargs: The keyword arguments used to build the query string

        :rtype: str
        :return: The result from the original ``get(...)`` function
        """
       
        print 'url:', url,

        if 'params' in kwargs:
            print 'get:',  kwargs['params'],

        result = self._get(url, **kwargs)

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(result.text.encode('UTF-8'))
            print 'Output saved to', f.name

        return result

    def mock_post(self, url, data, **kwargs):
        """
        This replaces ``requests.post``. It prints out post payload
        (``data``), passes the request along to the original
        ``get(...)`` function and then saves the result to a file

        :type url: str
        :param url: The URL of the resource being requested

        :type data: dict
        :param data: The data payload that will be sent via post
            to the server.

        :rtype: str
        :return: The result from the original ``get(...)`` function
        """

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

class Shaman(unittest2.TestCase):
    """
    The Shaman will help illuminate flaws in your code and
    help you to heal them.
    """

    class __metaclass__(type):
        """
        The ``lib.test.Shaman.generate`` function sets metadata on
        what functions the user wants to create. Then,
        ``__metaclass__`` reads that metadata and is the one
        that actually creates the new functions
        """
        def __new__(cls, name, bases, class_dict):
            def callback(function, args):
                try:
                    string_types = types.StringTypes  # Python2.x
                except AttributeError:
                    string_types = str  # Python3

                if isinstance(args, string_types):
                    return lambda self: function(self, args)
                else:
                    return lambda self: function(self, *args)

            if name != 'Shaman':
                for objName, obj in class_dict.items():
                    if hasattr(obj, 'shaman_generate_inputs'):
                        for id, input in obj.shaman_generate_inputs:
                            key = '%s_%s' % (obj.__name__, id)
                            class_dict[key] = callback(obj, input)
                        del class_dict[objName]
            return type.__new__(cls, name, bases, class_dict)

        def __init__(cls, name, bases, class_dict):
            if name != 'Shaman':
                lib.registry.register(test=cls)

    #: The spell that is being tested
    #:
    #: .. note::
    #:    You usually never have to set this value, it should get
    #:    detected automatically. However, if you **do** set this value
    #:    ``Shaman`` won't overwrite it
    spell = None

    #: An instantiated version of ``spell``.
    spell_obj = None

    @classmethod
    def setUpClass(cls):
        """
        A class-level fixture that gets called automatically by ``unittest2``;
        there should be no need to call this function directly.

        This fixture takes care of the following:
            * The module being tested is automatically detected
            * The following mocks are configured:
                * **state** -- creates a temporary storage for the spell's state
                * **config** -- a mock config that can be configured in the test and
                    "loaded" by the config
                * **web** -- overwrites ``lib.spell.BaseSpell.fetch`` with
                    a ``lib.test.WebMock`` function which intercepts
                    requests which are then served by predefined datafiles so
                    that the test can be run offline
        """

        spellRegistry = lib.registry.lookup_by_name(test=cls.__name__)
        root = spellRegistry['root']
        cls.state = dict()
        cls.config = dict()
        cls.queries = dict()
        cls.web = WebMock(os.path.join(root, 'test_data'))
        cls.patches = [cls.web.mock]
        lib.registry.collect()

        # Search for spell if one is not already provided
        # (a spell that is in the same directory)
        if cls.spell is None:
            try:
                cls.spell = spellRegistry['spell']
            except KeyError:
                raise ValueError(
                    'Unable to detect associated spell for: %s.%s'
                    % (inspect.getfile(cls), cls)
                )

        cls.spell_obj = cls.spell()

    @classmethod
    def generate(cls, *args, **kwargs):
        """
        A utility method that uses the arguments to duplicate the decorated
        test function

        :type args: list
        :param args: The positional arguments

        :type kwargs: dict
        :param kwargs: The keyword arguments

        The generated functions are named by taking the name of decorated function
        and then:

        * using numerically incrementing ids for input elements in ``*args``
        * using the keyword provided for the input elements in ``**kwargs``

        For example:

        .. code-block:: python

            @Shaman.generate('happy', 'sad', sleepy='Zzzz')
            def test_example(input):
                pass

        Would generate the following:

        .. code-block:: python

            def test_example_1(input='happy'):
                pass

            def test_example_2(input='sad'):
                pass

            def test_example_sleepy(input='Zzzz'):
                pass

        .. warning::
            The decorated/original function gets destroyed when
            the generated functions get created
        """

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

    @classmethod
    def collectQueries(cls):
        """
        Run the test (silently) and return the queries issued, along with the associated results

        :rtype: dict
        :return: A dictionary mapping input queries to expected output
        """
        clsObj = cls()
        clsObj.setUpClass()
        for attr in dir(clsObj):
            obj = getattr(clsObj, attr)
            if not attr.find('test_') and hasattr(obj, '__call__'):
                clsObj.setUp()
                obj()
        return clsObj.queries


    def setUp(self):
        pass

    def assertLooksLike(self, first, second, msg=None):
        """
            Compare ``first`` and ``second``, ignoring differences in
            whitespace and case

            :type first: str
            :param first: The first value to use in the comparison

            :type second: str
            :param second: The second value to use in the comparison

            :type msg: str or None
            :param msg: Use a custom error message if the values don't look alike

            :raises: ``AssertionError``
        """

        normalize = lambda string: re.sub(r'\s+', ' ', string).lower().strip()

        if normalize(first) != normalize(second):
            default_msg = (
                '%s\n<[---------- does not look like ----------]>\n%s'
                % (first, second)
            )
            msg = self._formatMessage(msg, default_msg)
            raise self.failureException(msg)

    def runTest(self):
        pass

    def query(self, query):
        """
            Pass query to spell with mocked functions enabled, returning the result

            :type query: str
            :param query: The query to give to the spell

            :returns: returns the result of the spell
            :rtype: str
        """
            
        for patch in self.patches:
            patch.start()

        score, cls, _query = self.spell_obj.parse(query)
        result, self.state = self.spell_obj.incantation(
            _query, self.config, self.state
        )

        for patch in self.patches:
            patch.stop()

        self.queries[query] = result

        return result

    def today(self, year, month, day):
        """
            Replace ``lib.spell.BaseSpell.today`` with a mock function
            which returns a constant date

            :type year: int
            :param year: ex: 2010

            :type month: int
            :param month: valid values are 1 (January) to 12 (December)

            :type day: int
            :param day: valid values are 1 - 31, depending on the month
        """
        patch = mock.patch(
            'lib.spell.BaseSpell.today',
            lambda self: datetime.date(year, month, day)
        )
        self.patches.append(patch)
