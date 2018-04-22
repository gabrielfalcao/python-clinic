# -*- coding: utf-8 -*-
from .serialization import OrderedDict
from .serialization import json


class ActiveRecord(OrderedDict):
    """This is just an :py:class:`~collections.OrderedDict` that is
    **always** bound to a :py:class:`~Storage` object.

    An **ActiveRecord** has all the features of a :py:class:`~dict` plus is has deterministic serialization thanks to its ordered nature.
    Beyond that, it can be saved, deleted, read from a path and
    even bound to other DAO instances, making it easy to store the
    same data in different backends.

    :param __dao__: a :py:class:`~python_clinic.dao.base.Storage` instance.
    :param kw: keyword-args to construct a dict
    """
    def __init__(self, __dao__, **kw):
        super(ActiveRecord, self).__init__(**kw)
        self.parent = __dao__

    def to_json(self, *args, **kw):
        return json.dumps(self, *args, **kw)

    def with_dao(self, dao):
        """creates a clone of the data within this :py:class:`~ActiveRecord`
        pointing to another
        :py:class:`~python_clinic.dao.base.Storage` instance.

        :param dao: an instance of :py:class:`~python_clinic.dao.base.Storage`
        :returns: an :py:class:`~ActiveRecord` instance
        """
        return ActiveRecord(dao, **self)

    def clone(self):
        return self.__class__(self.parent, **self.deepcopy())

    def save(self, key):
        """Persists the data within this :py:class:`~ActiveRecord` using the
        value under the given key.

        This is really just a **shortcut** to :py:meth:`~python_clinic.dao.base.Storage.persist` on
        the DAO in which this **ActiveRecord** is bound to.

        .. note:: the implementation of method might produce I/O side-effect

        :param key: a :py:class:`~str` :returns: a copy of this :py:class:`~ActiveRecord` with the exact data that was persisted.
        """
        return self.parent.persist(self, key=key)

    def delete(self, key):
        """Deletes the data within this :py:class:`~ActiveRecord` using the
        value under the given key.

        This is really just a **shortcut** to :py:meth:`~python_clinic.dao.base.Storage.delete` on
        the DAO in which this **ActiveRecord** is bound to.

        .. note:: the implementation of method might produce I/O side-effect

        :py:class:`~str` :returns: a copy of this :py:class:`~ActiveRecord` with the exact data that was persisted.
        """
        return self.parent.delete(self, key=key)

    @classmethod
    def from_data(cls, data, dao):
        return cls(dao, **data)

    @classmethod
    def from_object(cls, obj, dao):
        return cls.from_data(obj)

    @classmethod
    def from_path(cls, path, dao):
        """Reads JSON data from the given path

        :param path: a :py:class:`~pathlib.PurePath` or string
        :param dao: an instance of :py:class:`~python_clinic.dao.base.Storage` most likely a subclass
        :returns: an :py:class:`~python_clinic.dao.base.ActiveRecord`
        """
        obj = dao.get_object_from_path(path)
        return cls.from_object(obj, dao)


class Storage(object):
    """Base `DAO <https://en.wikipedia.org/wiki/Data_access_object>`_ class interface.

    This class can be easily inherited in order to implement other
    backends, for example file-system, Amazon S3 or DynamoDB.

    The initial implementation of this is
    :py:class:`~python_clinic.dao.base.Storage`
    """
    def __init__(self, *args, **kw):
        self.initialize(*args, **kw)

    def initialize(self, *args, **kw):
        raise NotImplementedError

    def get_namespace_path(self, namespace):
        raise NotImplementedError

    @classmethod
    def is_available(cls):
        """this classmethod must be implemented by subclasses and return True if all the dependencies for that particular backend to work are available.
        """
        raise NotImplementedError

    def clone(self, namespace):
        """creates a clone of this
        :py:class:`~python_clinic.dao.base.Storage`, pointing
        to the same root path but under another namespace.
        """

    def of(self, *args, **kw):
        """syntax sugar to :py:meth:`~clone`"""
        return self.clone(*args, **kw)

    def new(self, **kw):
        """creates a new :py:class:`~python_clinic.dao.base.ActiveRecord` with the given
        keyword-args"""
        return ActiveRecord(self, **kw)

    def iter_all(self, namespace):
        """scans the rootpath for all objects under the given namespace.

        :param namespace: :py:class:`~str`

        :returns: a generator of 2-item tuples of: :py:class:`~ActiveRecord` objects and a :py:class:`~str` of its source path in the file-system.
        """
        raise NotImplementedError

    def list_all(self, *args, **kw):
        """lists all records under a given namespace, Under the hood it calls :py:meth:`~iter_all` but returns a list of :py:class:`~ActiveRecord` rather than a 2-item tuple

        :param namespace: :py:class:`str`
        :param sort_by: :py:class:`str` with the name of the key to which sorting will be targetted to.
        :returns: a list of :py:class:`~ActiveRecord` objects with valid data from the objects yielded by iter_all
        """
        return self.iter_all(*args, **kw)

    def count(self, namespace):
        """returns the total object count in the given namespace

        :returns: an integer
        """
        raise NotImplementedError

    def retrieve_by(self, **lookup):
        """performs a lookup in the database based on the given key/values

        .. note:: ideally you should pass a single key/value pair in the lookup keyword args.

        :param lookup: keyword arguments used to build looku paths of files in the disk.
        :returns: a single :py:class:`~ActiveRecord` object for the first record found with the provided keyword arguments.
        """
        raise NotImplementedError

    def delete_all(self):
        """Intended for testing purposes only!

        **Deletes all files under the given namespace!!**

        .. warning:: calling this method will cause ALL data to be deleted.
        """
        raise NotImplementedError

    def build_persistence_path(self, key_value):
        """takes a 2-item tuple as per yielded by :py:meth:`~dict.items` and
        generates a valid file-system path in which the data could
        potentially be found.

        The given value is hashed with SHA1 so as to result in a valid filename.

        The concoction is comprised of: ``<root_path>/<namespace>/<key>/<sha1(value)>``

        :param key_value: a 2-item tuple
        :returns: :py:class:`~pathlib.Path`
        """
        raise NotImplementedError

    def persist(self, item, key):
        """persists an :py:class:`~ActiveRecord` by the given key.
        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~ActiveRecord`
        :param key: a :py:class:`~str` of a key within ``item`` that will be passed on to :py:meth:`~build_persistence_path` then onto :py:meth:`~persist_in_path`
        :returns: the item itself
        """

    def delete(self, item, key):
        """deletes an :py:class:`~ActiveRecord` by the given key.
        .. warning:: the given key must be present within the item

        :param item: an :py:class:`~ActiveRecord`
        :param key: a :py:class:`~str` of a key within ``item`` that will be passed on to :py:meth:`~build_persistence_path` then unlinked.
        :returns: the item itself
        """
        raise NotImplementedError
