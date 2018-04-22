# -*- coding: utf-8 -*-
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from botocore.exceptions import EndpointConnectionError
from pathlib import PurePath
from hashlib import sha1
from python_clinic import aws
from python_clinic import conf
from python_clinic.dao.base import Storage
from python_clinic.dao.base import ActiveRecord
from python_clinic.logs import get_logger

from .serialization import json

logger = get_logger(__name__)


def determine_bucket_name():
    return conf.get('dao', 's3', 'bucket_name', fallback=None)


def determine_namespace_prefix():
    return conf.get('dao', 's3', 'namespace', fallback=None)


class S3KeyNotFoundError(Exception):
    """Raised when a given key cannot be found in the given bucket
    """
    def __init__(self, s3_object):
        msg = 'could not find key {s3_object.key} in bucket {s3_object.bucket_name}'
        super(S3KeyNotFoundError, self).__init__(msg.format(**locals()))


class S3PutObjectFailed(Exception):
    """Raised when failed to write key to its s3 bucket
    """
    def __init__(self, bucket_name, key_name):
        msg = 'could not find key {key_name} in bucket {bucket_name}'
        super(S3PutObjectFailed, self).__init__(msg.format(**locals()))


class InvalidS3Contents(Exception):
    """Raised when no JSON data could be loaded from the given s3 key,
    either because the file does not exist of its content is not a
    valid JSON.
    """
    def __init__(self, path):
        msg = 'the path {} does not contain a valid json object'
        super(InvalidS3Contents, self).__init__(msg.format(path))


class InvalidKeyValue(Exception):
    """Raised when a non-string value as given as a key
    """
    def __init__(self, value, namespace, key):
        msg = 'invalid value {value} under keyspace {namespace}/{key}'
        super(InvalidKeyValue, self).__init__(msg.format(**locals()))


class ActiveS3Record(ActiveRecord):
    """Subclass of
    :py:class:`~python_clinic.dao.base.ActiveRecord` with extra
    features specific to file-based storage.
    """

    @classmethod
    def from_object(cls, s3_object, dao):
        """Reads JSON data from a s3 object

        :param s3_object: a :py:class:`~boto3.resources.factory.s3.ServiceResource`
        :param dao: an instance of :py:class:`~python_clinic.dao.files.S3Storage`
        :returns: an :py:class:`~python_clinic.dao.files.ActiveS3Record`
        """
        try:
            stream = s3_object.get()['Body']
        except ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                raise S3KeyNotFoundError(s3_object)

        data = json.load(stream)

        if not isinstance(data, dict):
            raise InvalidS3Contents(s3_object.key)

        return cls(dao, **data)

    @classmethod
    def from_path(cls, path, dao):
        """Reads JSON data from a key path

        :param path: a :py:class:`~pathlib.PurePath`
        :param dao: an instance of :py:class:`~python_clinic.dao.files.S3Storage`
        :returns: an :py:class:`~python_clinic.dao.files.ActiveS3Record`
        """
        s3_object = dao.get_object_from_path(str(path))
        return cls.from_object(s3_object, dao)


class S3StorageError(Exception):
    """Thrown when trying to persist data within an invalid namespace.

    Can be caused if trying to write using a
    :py:class:`~python_clinic.dao.base.Storage` without
    defining a namespace.
    """


class S3Storage(Storage):
    """S3-based DAO, similar to
    dictionaries as JSON in the file-system.

    This class is the first implementation of
    :py:class:`~python_clinic.dao.base.Storage`, is simple
    enough to ensure that our goals are achieved and can be further
    extended and refactored to leverage other storage backends that
    have a similar path-based storage mechanism.

    Usage:

    ::

        from python_clinic.dao.files import S3Storage

        dao = S3Storage("bucket-name")
        person1 = dao.of("users").new(id=1, email='foo@bar.com')
        dao.persist(person1, 'id')

    this create the key: ``python-clinic/users/id/356a192b7913b04c54574d18c28d46e6395428ab``

    because ``SHA1("1") == "356a192b7913b04c54574d18c28d46e6395428ab"``

    and the content of ``s3://bucket-name/python-clinic/users/id/356a192b7913b04c54574d18c28d46e6395428ab``
    would be:

    ::

        {
            "id": "356a192b7913b04c54574d18c28d46e6395428ab",
            "email": "foo@bar.com"
        }
    """

    @classmethod
    def is_available(cls):
        bucket_name = determine_bucket_name()
        if not bucket_name:
            return False
        try:
            bucket = aws.bucket(bucket_name)
            list(bucket.objects.all())  # try to list bucket
            return True
        except (NoCredentialsError, EndpointConnectionError) as error:
            msg = (
                'S3Storage backend is not available: %s'
            )
            logger.warning(msg, error)
            return False
        except ClientError as error:
            msg = (
                'S3Storage backend is not available for bucket %s: %s'
            )
            logger.warning(msg, bucket_name, error)
            return False
        except Exception:
            msg = (
                'S3Storage backend is not available due to an unexpected '
                'error when accessing the bucket %s'
            )
            logger.exception(msg, bucket_name)
            return False

    def initialize(self, bucket_name=None, namespace='', fallback_prefix='python-clinic'):
        if not bucket_name:
            bucket_name = determine_bucket_name()

        if not namespace:
            namespace = ''

        self.bucket_name = bucket_name
        self.prefix = (determine_namespace_prefix() or fallback_prefix).strip('/')
        self.__namespace = namespace

    @property
    def namespace(self):
        ns = '{}/{}'.format(self.prefix, self.__namespace)
        return ns

    @property
    def path(self):
        return PurePath(self.namespace)

    @property
    def session(self):
        return aws.session()

    @property
    def s3(self):
        return aws.resource('s3')

    @property
    def bucket(self):
        return self.s3.Bucket(self.bucket_name)

    def get_object_from_path(self, key_path):
        obj = self.s3.Object(self.bucket_name, str(key_path))
        return obj

    def clone(self, namespace):
        """creates a clone of this S3Storage, pointing to the same root path
        but under another namespace."""
        return S3Storage(namespace=namespace, bucket_name=self.bucket_name, fallback_prefix=self.prefix)

    def new(self, **kw):
        """creates a new :py:class:`~python_clinic.dao.files.ActiveS3Record` with the given
        keyword-args"""
        result = ActiveS3Record(self, **kw)
        return result

    def ensure_prefixed(self, namespace):
        namespace = namespace.lstrip('/')
        if not namespace.startswith(self.prefix):
            namespace = '{}/{}'.format(self.prefix, namespace)

        return namespace

    def iter_all(self, namespace=''):
        """scans the rootpath for all objects under the given namespace.

        :param namespace: :py:class:`~str`

        :returns: a generator of 2-item tuples of: :py:class:`~python_clinic.dao.files.ActiveS3Record` objects and a :py:class:`~str` of its source path in the file-system.
        """
        namespace = self.ensure_prefixed(namespace)
        for s3_object in self.bucket.objects.filter(Prefix=namespace):
            path = s3_object.key
            try:
                yield ActiveS3Record.from_object(s3_object, self), path
            except (InvalidS3Contents, S3KeyNotFoundError):
                continue

    def count(self, namespace=''):
        """
        :returns: an integer with the total object count in the given namespace
        """
        namespace = self.ensure_prefixed(namespace)
        return sum(1 for _ in self.bucket.objects.filter(Prefix=namespace))

    def list_all(self, namespace=''):
        """lists all records under a given namespace, Under the hood it calls :py:meth:`~iter_all` but returns a list of :py:class:`~python_clinic.dao.files.ActiveS3Record` rather than a 2-item tuple

        :param namespace: :py:class:`~str`
        :returns: a list of :py:class:`~python_clinic.dao.files.ActiveS3Record` objects with valid data from json files found
        """
        return [record for record, path in self.iter_all(namespace)]

    def retrieve_by(self, **lookup):
        """performs a lookup in the database based on the given key/values

        .. note:: ideally you should pass a single key/value pair in
            the lookup keyword args.

        :param lookup: keyword-arguments used to build looku paths of files in the disk.
        :returns: a single :py:class:`~python_clinic.dao.files.ActiveS3Record` object for the first record found with the provided keyword arguments.

        """
        lookup_paths = list(map(str, (map(self.build_persistence_path, filter(all, lookup.items())))))

        for path in lookup_paths:
            try:
                return ActiveS3Record.from_path(path, self)
            except (InvalidS3Contents, S3KeyNotFoundError):
                continue

    def delete_all(self, namespace):
        """Intended for testing purposes only!

        **Deletes all files under the given namespace!!**

        .. warning:: this recursive deletes ALL valid json files under the ``root_path`` of this :py:class:`~python_clinic.dao.files.S3Storage`
        """
        namespace = self.ensure_prefixed(namespace)
        for s3_object in self.bucket.objects.filter(Prefix=namespace):
            result = s3_object.delete()
            logger.warning('deleting object %s: %s', s3_object, result)

    @property
    def keyspace(self):
        return self.path

    def build_persistence_path(self, key_value):
        """takes a 2-item tuple as per yielded by :py:meth:`~dict.items` and
        generates a valid s3 key name in which the data could potentially
        be found.

        The given value is hashed with SHA1 so as to result in a valid filename.

        The concoction is comprised of: ``<root_path>/<namespace>/<key>/<sha1(value)>``

        :param key_value: a 2-item tuple
        :returns: :py:class:`str` derived from a :py:class`~pathlib.PurePath`

        :raises: :py:class:`~python_clinic.dao.files.S3StorageError` if no namespace as defined. To remedy that always make sure to use the file-storage like: ``storage.of("my-namespace")`` where the given namespace is a valid directory name.

        """
        key, value = key_value
        if not self.namespace:
            raise S3StorageError('cannot persist without a namespace')

        if not isinstance(value, (str, bytes)):
            raise InvalidKeyValue(value, self.namespace, key)

        elif isinstance(value, str):
            value = value.encode('utf-8')

        value = sha1(value).hexdigest()
        return str(self.keyspace.joinpath(key, value))

    def iter_paths(self, namespace=''):
        namespace = self.ensure_prefixed(namespace)
        for s3_object in self.bucket.objects.filter(Prefix=namespace):
            yield s3_object.key

    def list_paths(self, namespace=''):
        return list(self.iter_paths(namespace))

    def persist_in_path(self, item, path):
        """persists an :py:class:`~python_clinic.dao.files.ActiveS3Record` in the given ``path``.

        - creates the parent directory if it doesn't already exist
        - json-serializes the data within :py:class:`~python_clinic.dao.files.ActiveS3Record` data
        - writes it to the disk at the given ``path``

        :param item: an :py:class:`~python_clinic.dao.files.ActiveS3Record`
        :param path: a :py:class:`~pathlib.PurePath`
        :returns: the item itself
        """
        s3_object = self.get_object_from_path(path)

        body = json.dumps(item, default=str)
        response = s3_object.put(Body=body)
        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if status_code != 200:
            raise S3PutObjectFailed(s3_object)

        return item

    def persist(self, item, key):
        """persists an :py:class:`~python_clinic.dao.files.ActiveS3Record` by the given key.

        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~python_clinic.dao.files.ActiveS3Record`
        :param key: a :py:class:`~str` of a key within ``item`` that will be passed on to :py:meth:`~build_persistence_path` then onto :py:meth:`~persist_in_path`
        :returns: a safe copy of the given item
        """

        try:
            value = item[key]
        except KeyError as e:
            logger.warning('%s on %s', e, item.to_json(indent=2))
            return

        dst = self.build_persistence_path((key, value))
        try:
            self.persist_in_path(item, dst)
        except (IOError, OSError) as e:
            logger.warning('could not persist %s: %s', dst, e)
            return

        return item.with_dao(self)

    def delete(self, item, key):
        """deletes an :py:class:`~python_clinic.dao.files.ActiveS3Record` by the given key.

        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~python_clinic.dao.files.ActiveS3Record`
        :param key: a :py:class:`~str` of a key within ``item`` that will be passed on to :py:meth:`~build_persistence_path` then unlinked.
        :returns: a safe copy of the given item
        """
        try:
            value = item[key]
        except KeyError as e:
            logger.warning('%s on %s', e, item.to_json(indent=2))
            return

        dst = self.build_persistence_path((key, value))
        result = self.s3.delete_object(Bucket=self.bucket_name, Key=dst)
        logger.warning('deleting object %s/%s: %s', self.bucket_name, dst, result)

        return item.with_dao(self)
