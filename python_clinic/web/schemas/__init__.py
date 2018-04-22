# -*- coding: utf-8 -*-
import io
import pathlib

from flask import request
from flask import Response
from flask_restplus.reqparse import RequestParser
from jsonschema import ValidationError
from jsonschema import validate
# from werkzeug.exceptions import BadRequest

from python_clinic.web.logs import logger
from python_clinic.dao import json


class SchemaValidationError(Exception):
    """A more straightforward and less verbose exception that is raise
    whenever a :py:class:`jsonschema.ValidationError` is capture.

    :param verror: an instance of :py:class:`jsonschema.ValidationError`
    """
    def __init__(self, verror):
        path = '.'.join(map(str, verror.path))
        msg = 'in path {path}: {verror.message}'
        self.original = verror
        super(SchemaValidationError, self).__init__(msg.format(**locals()))


def json_response(data, status_code=200, headers=None, indent=None):
    body = json.dumps(data, indent=indent)
    headers = dict(headers or {})
    headers['Content-Type'] = 'application/json'
    return Response(body, status_code, headers=headers)


def schema_response(schema, data, status_code=200, headers=None, indent=None, force_validation=False):
    """same as :py:func:`json_response` but validates the given body against a json schema
    """
    try:
        validate(data, schema)
    except ValidationError as e:
        e = SchemaValidationError(e)
        msg = 'JSON response does not validate against schema - {}'.format(e)
        if force_validation:
            logger.warning(msg)
            raise e
        else:
            logger.warning('JSON response does not validate against schema - {}'.format(msg))

    return json_response(data, status_code, headers, indent)


def schema_parser(schema, default=None, force_validation=False):
    """generates a :py:class:`~flask_restplus.reqparse.RequestParser`
    """
    parser = RequestParser()
    convert = JsonRequest(schema, force_validation)
    parser.add_argument(
        'payload',
        location='json',
        type=convert.from_string,
        default=json.dumps(default, indent=2)
    )
    return parser


class JsonSchemaHttpPair(object):
    """Unified declaration of JSON schemas for a particular endpoint's
    HTTP request and possible responses.


    """
    def __init__(self, request_file, response_files, force_validation=False):
        self.request_schema = from_file(request_file)
        self.response_schemas = dict([(k, from_file(v)) for k, v in response_files.items()])
        self.force_validation = force_validation

    @property
    def request(self):
        return JsonRequest(self.request_schema, force_validation=self.force_validation)

    @property
    def response(self):
        return JsonResponse(self.response_schemas, force_validation=self.force_validation)


def from_file(name):
    source_path = pathlib.Path(__file__).parent
    schema_path = source_path.joinpath(name)

    with io.open(str(schema_path)) as stream:
        schema = json.load(stream)

    return schema


class JsonRequest(object):
    """Handlers the parsing of a :py:class:`flask.Request` and automatic
    validation against a json-schema.
    """
    def __init__(self, schema, force_validation):
        self.schema = schema
        self.force_validation = force_validation

    def parse(self):
        return self.from_string(request.data)

    def from_string(self, string):
        if not string:
            string = '{}'

        data = json.loads(string)
        while not isinstance(data, (dict, list)):
            try:
                data = json.loads(data)
            except Exception:
                break

        return self.validate_schema(data)

    def log(self, *args, **kw):
        if self.force_validation:
            do_log = logger.warning
        else:
            do_log = logger.error

        return do_log(*args, **kw)

    def validate_schema(self, data):
        try:
            validate(data, self.schema)
        except ValidationError as e:
            e = SchemaValidationError(e)
            self.log('JSON request does not validate against schema - %s', e)
            if self.force_validation:
                raise e

        return data


class JsonResponse(object):
    """Handlers the parsing of a :py:class:`flask.Response` and automatic
    validation a set ofjson-schemas mapped to different status codes.

    This allows for validationg the json schema within the response in
    different cases. (i.e.: even 400 requests should return valid jsons expected by its clients)
    """
    def __init__(self, schemas, force_validation):
        self.schemas = schemas
        self.force_validation = force_validation

    @classmethod
    def from_file(cls, name):
        return cls(from_file(name))

    def to_flask(self, data, status_code=200, *args, **kw):
        schema = self.schemas.get(int(status_code))
        if not schema:
            return json_response(data, status_code, *args, **kw)

        return schema_response(schema, data, status_code, force_validation=self.force_validation, *args, **kw)

    def __call__(self, *args, **kw):
        return self.to_flask(*args, **kw)
