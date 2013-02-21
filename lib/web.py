import logging
import requests
import StringIO
from xml.etree import ElementTree as etree

FETCH_FORMATS = {
    'raw': lambda request: request.text,
    'json': lambda request: request.json(),
    'xml': lambda request: etree.parse(StringIO.StringIO(request.text.encode('UTF-8')))._root
}

def fetch(url, post=None, get=None, format='raw'):
    try:
        if post:
            request = requests.post(url, data=post)
        if get:
            request = requests.get(url, params=get)
        else:
            request = requests.get(url)

        request.raise_for_status()

        try:
            return FETCH_FORMATS[format](request)
        except KeyError:
            raise ValueError('Invalid format: %s' % format)

    except requests.exceptions.HTTPError, e:
        raise
