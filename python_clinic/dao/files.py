# -*- coding: utf-8 -*-
import io
import os

from hashlib import sha1
from pathlib import Path
from python_clinic import conf
from python_clinic.dao.base import Storage
from python_clinic.dao.base import ActiveRecord
from python_clinic.logs import get_logger

from .serialization import json

logger = get_logger(__name__)


def determine_file_storage_path():
    storage_path = conf.get('dao', 'file_system', 'storage_path', throw=True)
    return Path(storage_path)


class InvalidFileContents(Exception):
    """Raised when no JSON data could be loaded from the given path,
    either because the file does not exist of its content is not a
    valid JSON.
    """
    def __init__(self, path):
        msg = 'the path {} does not contain a valid json object'
        super(InvalidFileContents, self).__init__(msg.format(path))


class InvalidKeyValue(Exception):
    """Raised when a non-string value as given as a key
    """
    def __init__(self, value, namespace, key):
        msg = 'invalid value {value} under keyspace {namespace}/{key}'
        super(InvalidKeyValue, self).__init__(msg.format(**locals()))


class ActiveFileRecord(ActiveRecord):
    """Subclass of
    :py:class:`~python_clinic.dao.base.ActiveRecord` with extra
    features specific to file-based storage.
    """

    @classmethod
    def from_object(cls, stream, dao):
        """Reads JSON data from a stream

        :param stream: a file-like object
        :param dao: an instance of :py:class:`~python_clinic.dao.files.FileStorage`
        :returns: an :py:class:`~python_clinic.dao.files.ActiveFileRecord`
        """
        try:
            data = json.load(stream)
        except Exception:
            raise InvalidFileContents(stream.path)

        if not isinstance(data, dict):
            raise InvalidFileContents(stream.path)

        return cls(dao, **data)

    @classmethod
    def from_path(cls, path, dao):
        """Reads JSON data from a file-system path

        :param path: a :py:class:`~pathlib.Path`
        :param dao: an instance of :py:class:`~python_clinic.dao.files.FileStorage`
        :returns: an :py:class:`~python_clinic.dao.files.ActiveFileRecord`
        """
        stream = dao.get_object_from_path(path)
        return cls.from_object(stream, dao)


class FileStorageError(Exception):
    """Thrown when trying to persist data within an invalid namespace.

    Can be caused if trying to write using a
    :py:class:`~python_clinic.dao.base.Storage` without
    defining a namespace.
    """


class FileStorage(Storage):
    """File-based `DAO <https://en.wikipedia.org/wiki/Data_access_object>`_ that stores
    dictionaries as JSON in the file-system.

    This class is the first implementation of
    :py:class:`~python_clinic.dao.base.Storage`, is simple
    enough to ensure that our goals are achieved and can be further
    extended and refactored to leverage other storage backends that
    have a similar path-based storage mechanism.

    Usage:

    ::

        from python_clinic.dao.files import FileStorage

        dao = FileStorage("~/my-storage")
        person1 = dao.of("users").new(id=1, email='foo@bar.com')
        dao.persist(person1, 'id')

    this create the file: ``~/my-storage/users/id/356a192b7913b04c54574d18c28d46e6395428ab``

    because ``SHA1("1") == "356a192b7913b04c54574d18c28d46e6395428ab"``

    and the content of ``~/my-storage/users/id/356a192b7913b04c54574d18c28d46e6395428ab``
    would be:

    ::

        {
            "id": "356a192b7913b04c54574d18c28d46e6395428ab",
            "email": "foo@bar.com"
        }
    """
    @classmethod
    def is_available(cls):
        try:
            path = determine_file_storage_path()
        except conf.ConfigKeyNotFound as e:
            return False

        available = path.parent.is_dir()
        if not available:
            msg = (
                'FileStorage is not available because the parent folder '
                'of the configured `dao.file_system.storage_path` '
                'does not exist or is not a directory: %s'
            )
            logger.warning(msg, path.parent)

        return available

    def initialize(self, root_path=None, namespace=''):
        if root_path is None:
            root_path = determine_file_storage_path()

        self.path = root_path
        self.namespace = namespace

    def get_namespace_path(self, namespace):
        return self.path.joinpath(namespace)

    def clone(self, namespace):
        """creates a clone of this FileStorage, pointing to the same root path
        but under another namespace."""
        return FileStorage(namespace=namespace, root_path=self.path)

    def new(self, **kw):
        """creates a new :py:class:`~python_clinic.dao.files.ActiveFileRecord` with the given
        keyword-args"""
        result = ActiveFileRecord(self, **kw)
        return result

    def iter_paths(self, namespace=''):
        namespace = namespace.lstrip('/')
        src = self.get_namespace_path(namespace)
        for path in src.glob('**/*'):
            if path.is_file():
                yield path

    def get_object_from_path(self, path):
        return io.open(str(path), 'r')

    def list_paths(self, namespace=''):
        return list(self.iter_paths(namespace))

    def iter_all(self, namespace):
        """scans the rootpath for all objects under the given namespace.

        :param namespace: :py:class:`~str`

        :returns: a generator of 2-item tuples of: :py:class:`~python_clinic.dao.files.ActiveFileRecord` objects and a :py:class:`~str` of its source path in the file-system.
        """
        for path in self.iter_paths(namespace):
            if path.is_file():
                try:
                    yield ActiveFileRecord.from_path(path, self), path
                except (InvalidFileContents, FileNotFoundError):
                    continue

    def count(self, namespace):
        """
        :returns: an integer with the total object count in the given namespace
        """
        src = self.get_namespace_path(namespace)
        return len(list(src.glob('**/*')))

    def list_all(self, namespace):
        """lists all records under a given namespace, Under the hood it calls :py:meth:`~iter_all` but returns a list of :py:class:`~python_clinic.dao.files.ActiveFileRecord` rather than a 2-item tuple

        :param namespace: :py:class:`~str`
        :returns: a list of :py:class:`~python_clinic.dao.files.ActiveFileRecord` objects with valid data from json files found
        """
        return [record for record, path in self.iter_all(namespace)]

    def retrieve_by(self, **lookup):
        """performs a lookup in the database based on the given key/values

        .. note:: ideally you should pass a single key/value pair in
            the lookup keyword args.

        :param lookup: keyword-arguments used to build looku paths of files in the disk.
        :returns: a single :py:class:`~python_clinic.dao.files.ActiveFileRecord` object for the first record found with the provided keyword arguments.

        """
        lookup_paths = map(self.build_persistence_path, filter(all, lookup.items()))
        for path in lookup_paths:
            try:
                return ActiveFileRecord.from_path(path, self)
            except (InvalidFileContents, FileNotFoundError):
                continue

    def delete_all(self, namespace):
        """Intended for testing purposes only!

        **Deletes all files under the given namespace!!**

        .. warning:: this recursive deletes ALL valid json files under the ``root_path`` of this :py:class:`~python_clinic.dao.files.FileStorage`
        """
        result = []
        for record, path in self.iter_all(namespace):
            if path.is_file():
                path.unlink()
                result.append(record)

        return result

    @property
    def keyspace(self):
        return self.get_namespace_path(self.namespace)

    def build_persistence_path(self, key_value):
        """takes a 2-item tuple as per yielded by :py:meth:`~dict.items` and
        generates a valid file-system path in which the data could
        potentially be found.

        The given value is hashed with SHA1 so as to result in a valid filename.

        The concoction is comprised of: ``<root_path>/<namespace>/<key>/<sha1(value)>``

        :param key_value: a 2-item tuple
        :returns: :py:class:`~pathlib.Path`

        :raises: :py:class:`~python_clinic.dao.files.FileStorageError` if no namespace as defined. To remedy that always make sure to use the file-storage like: ``storage.of("my-namespace")`` where the given namespace is a valid directory name.
        """
        key, value = key_value
        if not self.namespace:
            raise FileStorageError('cannot persist without a namespace')

        if not isinstance(value, (str, bytes)):
            raise InvalidKeyValue(value, self.namespace, key)

        elif isinstance(value, str):
            value = value.encode('utf-8')

        value = sha1(value).hexdigest()
        return self.keyspace.joinpath(key, value)

    def persist_in_path(self, item, path):
        """persists an :py:class:`~python_clinic.dao.files.ActiveFileRecord` in the given ``path``.

        - creates the parent directory if it doesn't already exist
        - json-serializes the data within :py:class:`~python_clinic.dao.files.ActiveFileRecord` data
        - writes it to the disk at the given ``path``

        :param item: an :py:class:`~python_clinic.dao.files.ActiveFileRecord`
        :param path: a :py:class:`~pathlib.Path`
        :returns: the item itself
        """
        if not path.parent.is_dir():
            path.parent.mkdir(parents=True)

        with io.open(str(path), 'w') as stream:
            stream.write(json.dumps(item, default=str))
            stream.flush()
            os.fsync(stream.fileno())

        return item

    def persist(self, item, key):
        """persists an :py:class:`~python_clinic.dao.files.ActiveFileRecord` by the given key.

        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~python_clinic.dao.files.ActiveFileRecord`
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
        """deletes an :py:class:`~python_clinic.dao.files.ActiveFileRecord` by the given key.

        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~python_clinic.dao.files.ActiveFileRecord`
        :param key: a :py:class:`~str` of a key within ``item`` that will be passed on to :py:meth:`~build_persistence_path` then unlinked.
        :returns: a safe copy of the given item
        """
        try:
            value = item[key]
        except KeyError as e:
            logger.warning('%s on %s', e, item.to_json(indent=2))
            return

        dst = self.build_persistence_path((key, value))
        try:
            dst.unlink()
        except (IOError, OSError) as e:
            logger.warning('could not delete %s: %s', dst, e)
            return

        return item.with_dao(self)
