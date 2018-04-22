# -*- coding: utf-8 -*-
import requests

from hashlib import sha1
from flask import request
from flask import Response
from functools import wraps
from werkzeug.contrib.cache import FileSystemCache

from python_clinic import conf
from python_clinic.dao import json
from python_clinic.dao import OrderedDict
from python_clinic.logs import get_logger


logger = get_logger(__name__)


def normalize_header_name(name):
    return '-'.join([w.strip().title() for w in name.split('-')])


def deterministic_headers(headers):
    items = sorted(dict(headers).items(), key=lambda kv: kv[0])
    return OrderedDict([(normalize_header_name(k), v) for k, v in items])


def serialize_response(response):
    if not response:
        return None

    return json.dumps({
        'data': response.data,
        'status_code': response.status_code,
        'headers': deterministic_headers(response.headers),
    })


def deserialize_requests_response(response_data):
    if not response_data:
        return None
    response = requests.Response()
    response.raw = response_data['data']
    response.status_code = response_data['status_code']
    response.headers.update(deterministic_headers(response_data['headers']))
    return response


def deserialize_flask_response(response_data):
    if not response_data:
        return None

    return Response(
        response_data['data'],
        response_data['status_code'],
        headers=response_data['headers']
    )


class InvalidApiRoute(Exception):
    def __init__(self, name):
        mapping_file = __file__
        msg = 'no mapping found for route "{name}" in {mapping_file}'
        super(InvalidApiRoute, self).__init__(msg.format(**locals()))


class HttpBaseCache(object):
    def __init__(self, cache_dir=None, threshold=None, default_timeout=None):
        params = {
            'cache_dir': cache_dir or conf.get('caching', 'directory', fallback='/tmp/pc-cache'),
            'threshold': threshold or conf.get_int('caching', 'high_water_mark', fallback=500),
            'default_timeout': default_timeout or conf.get_int('caching', 'timeout', fallback=30),
        }
        self.db = FileSystemCache(**params)

    def generate_cache_key(self, method, url, headers):
        string = json.dumps(OrderedDict([
            ('method', method),
            ('url', url),
            ('headers', deterministic_headers(headers)),
        ]))
        return sha1(string).hexdigest()

    def get_raw(self, method, url, headers):
        if method.upper() != 'GET':  # only cache if method is GET
            return None

        key = self.generate_cache_key(method, url, headers)
        return self.db.get(key)

    def set(self, method, url, headers, response):
        if method.upper() != 'GET':  # only cache if method is GET
            return response

        key = self.generate_cache_key(method, url, headers)
        self.db.set(key, serialize_response(response))


class HttpClientCache(HttpBaseCache):
    def get(self, method, url, headers):
        cached = self.get_raw(method, url, headers)
        return deserialize_requests_response(cached)


class HttpServerCache(HttpBaseCache):
    def get(self, method, url, headers):
        cached = self.get_raw(method, url, headers)
        return deserialize_flask_response(cached)

    def endpoint(self, callback):
        @wraps(callback)
        def decorator(*args, **kw):
            method = request.method
            url = request.path
            headers = dict(request.headers)

            cached = self.get(method, url, headers)
            if cached:
                return cached

            response = callback(*args, **kw)
            self.set(method, url, headers, response)
            return response

        return decorator
