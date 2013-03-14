import os
import re
import inspect
import datetime
import requests

from io import StringIO
from xml.etree import ElementTree as ETree

import lib.registry

class _BaseSpellMeta(type):
    """
    This is used to override the default metaclass to intercept
    the class creation. It first registers the subclass' info
    before passing control back to the normal flow
    """
    def __init__(cls, name, bases, class_dict):
        if name != 'BaseSpell':
            lib.registry.register(spell=cls)
BaseSpellMeta = _BaseSpellMeta('BaseSpell', (object,), {})

class BaseSpell(BaseSpellMeta):
    """ As the name implies, this class provides a base functionality for spells.  """

    #: How much weight / relevance should be assigned. Spells with
    #: larger weights are preferred over ones with smaller weights. Defaults
    #: to ``-inf``
    weight = float('-inf')

    #: A string which will be compiled into a regular expression
    #: with the ``RE.VERBOSE`` flag. Queries matching ``pattern`` and not
    #: excluded by the ``blacklist`` will be sent to this spell for processing,
    #: in order of their weight. Defaults to ``$a`` which will never match
    #: anything.
    pattern = '$a'  # Will never match anything

    #: A string which, like ``pattern``, will be compiled into a
    #: regular expression with the ``RE.VERBOSE`` flag. This will prevent any
    #: queries from being matched to the spell, even if they match the
    #: defined ``pattern``. Defaults to ``$a`` which will never match anything.
    blacklist = '$a'  # Ditto

    #: A ``dict`` that defines the configuration values that are required
    #: for this spell. The dictionary must be of the following format:
    #:
    #: .. code-block:: Python
    #:
    #:    {
    #:        'key1': type1,
    #:        'key2': type2,
    #:        ...
    #:        'keyN': typeN 
    #:    }
    #:
    #: When starting up, Troz will check to make sure that those
    #: keys are defined in the config and will convert the values
    #: to the appropriate types.
    #:
    #: To define an enumeration of possible values, define a
    #: list where where the first element is the type, followed
    #: by the possible values
    #:
    #: For example:
    #:
    #: .. code-block:: Python
    #:
    #:    {
    #:        'security.mode': [str, 'high', 'medium', 'low', 'none']
    #:    }
    #:
    #: Dotted notation is used to specify sections and subvalues.
    #: Nested values are not supported
    config = dict()

    #: :returns: date a object preset to today
    #: :rtype: ``datetime.date``
    today = datetime.date.today

    def XML(request):
        if request.text:
            try:
                return ETree.fromstring(request.text)
            except UnicodeEncodeError:
                return ETree.fromstring(request.text.encode('UTF-8'))
        else:
            return ETree.ElementTree()

    fetchFormats = {
        'raw': lambda request: request.text,
        'json': lambda request: request.text and request.json() or {},
        'xml': XML
    }

    def __init__(self):
        self.pattern = re.compile(self.pattern, re.IGNORECASE | re.VERBOSE)
        self.blacklist = re.compile(self.blacklist, re.IGNORECASE | re.VERBOSE)


    def fetch(self, url, post=None, get=None, format='raw'):
        """
        Retrieve and return a web resource

        :type url: str
        :param url: The URL of the resource to retrieve

        :type post: dict
        :param post: If provided the retrieval will be
            done via a ``POST`` command, using the values
            provided here as the payload

        :type get: dict
        :param get: If provided the retrieval will be
            done via a ``GET`` command, using the values
            provided here to build the query string

        :type format: str
        :param format: Once the resource has been retrieved
            it will be decoded according to the value
            provided.

        Valid values for **format** are:
            * **raw** -- return the result without any post-processing. Returns a ``str``
            * **json** -- decode the result as a JSON; returns a ``dict``
            * **xml** -- decode the result as XML. Returns an ``ElementTree`` object

        :returns: The result retrieved from the resource decoded with
            the post-processor specified in ``format``
        :rtype: `mixed`
        :raises: ``ValueError``, ``HTTPError``
        """
        try:
            if post:
                request = requests.post(url, data=post)
            if get:
                request = requests.get(url, params=get)
            else:
                request = requests.get(url)

            request.raise_for_status()

            try:
                return self.fetchFormats[format](request)
            except KeyError:
                raise ValueError('Invalid format: %s' % format)

        except requests.exceptions.HTTPError:
            raise

    def parse(self, query):
        """
        Parses a query and returns the result consisting of three values:
            * **score**: By default, this is equal to ``self.weight``
            * **spell**: The current spell object (``self``)
            * **match**: The portion of the string that matched.
                If there is a regular expression group defined in ``self.pattern``,
                then the first matching group is returned

        :type query: str
        :param query: The query to parse
        :returns: a tuple of (`score`, `spell`, `query`)
        :rtype: ``tuple(float, self, str)``
        """
        match = self.pattern.match(query)
        if match:
            if self.blacklist.match(query):
                return None, self, float('-inf')
            groups = match.groups()
            if groups:
                return self.weight, self, groups[0]
            else:
                return self.weight, self, query[match.start():match.end()]
        return float('-inf'), self, ''

    def incantation(self, query, config, state):
        """
        :type query: str
        :param query: The user's query that was processed by ``lib.spell.BaseSpell.parse``
        
        :type config: dict
        :param config: The user configuration that is stored in ``settings.conf``

        :type state: dict
        :param state: A storage object that can be used to persist data
            between executions

        :returns: `result`, `state`
        :rtype: ``str``, ``dict``
        """
        raise NotImplementedError("This must be provided by the spell!")

    def __str__(self):
        return self.__class__.__name__
