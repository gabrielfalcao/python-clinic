# -*- coding: utf-8 -*-
import re
import pendulum
from python_clinic import conf

DEFAULT_TIMEZONE = 'America/New_York'
DEFAULT_LOCALE = 'en'


class DateEngine(object):
    """high-level abstraction to python's own :py:mod:`datetime.datetime` with one big difference: it uses `pendulum <https://pendulum.eustace.io/docs/>`_ under the hood.

    Also includes useful methods to parse dates from various formats
    and generate correct ISO formats.
    """
    def __init__(self, timezone=None, locale=None):
        self.timezone = timezone or conf.get('app', 'TIMEZONE', fallback=DEFAULT_TIMEZONE)
        self.locale = locale or conf.get('app', 'DATETIME_LOCALE', fallback=DEFAULT_LOCALE)

    def parse(self, string):
        """parses pretty much any time format into a :py:class:`~datetime.datetime`-like instance instance
        """
        return pendulum.parse(string, tz=self.timezone)

    def now(self):
        """returns a datetime object with the current time, based on Python Clinic's configured timezone
        """
        return pendulum.datetime.now()

    def utcnow(self):
        """returns the current UTC datetime
        """
        return pendulum.utcnow()

    def pretty_now(self):
        """shortcut to return the current timezone's time using the format ``%Y-%m-%dT%H:%M:%S.%f``
        """
        return self.prettify(self.now())

    @classmethod
    def prettify(self, datetime):
        """Utility method to format any datetime object in a string with the format ``%Y-%m-%dT%H:%M:%S.%f``
        """
        return datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")

    def __call__(self, *args, **kw):
        """instantiates a datetime-like object
        """
        return pendulum.datetime(*args, **kw)


datetime = DateEngine()


def any_of(*items):
    """simple algorithm to return the first of the given values that resolves to a positive boolean
    """
    for item in items:
        if bool(item):
            return item


def enum(name, items):
    """creates a class with the given name and key/values as members
    :param name: a string
    :param items: a list of key/value tuple pairs (or the result from :py:meth:`dict.items`
    """
    return type(name, (object, ), dict([(k, k) for k in map(str, items)]))


def slugify(name, repchar='-'):
    """slugifies a string
    """
    return re.sub(r'[\W\s]+', repchar, name).lower()
