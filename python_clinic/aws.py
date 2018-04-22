# -*- coding: utf-8 -*-
import boto3
import io
import os
import pathlib

from configparser import ConfigParser

from python_clinic import conf
from python_clinic.util import any_of
from python_clinic.logs import get_logger


"""High-level access to Python Clinic's AWS resources based on the config yaml.


Example config:

.. code:: yaml

   boto3:
     session_config:
       aws_access_key_id: null
       aws_secret_access_key: null
       aws_session_token: null
       region_name: us-east-1
       profile_name: python-clinic


.. note:: The key/values under ``boto3.session_config`` are requivalent to the keyword args of :py:class:`~boto3.session.Session`. Make sure you **only pass valid arguments**.
"""


logger = get_logger(__name__)


def wipe_aws_environment_variables():
    for key in list(os.environ.keys()):
        if key.startswith('AWS_'):
            value = os.getenv(key)
            logger.debug('unset %s (%s)', key, value)
            del os.environ[key]


def get_session_config():
    config = conf.get_dict('boto3', 'session_config')
    if config:
        wipe_aws_environment_variables()

    return config


def session(config=None):
    """automatically reads :ref:`the aws config <aws config>` including :ref:`profile <aws profile>` and  :ref:`credentials <aws credentials>`
    :returns: an instance of :py:class:`boto3.Session`
    """
    if not config:
        config = get_session_config()

    return boto3.Session(**config)


def resource(name, config=None):
    """auto-loads a session :py:func:`~python_clinic.aws.session`
    :returns: a :py:meth:`boto3.Session.resource`
    """
    return session(config).resource(name)


def determine_default_bucket_name():
    """tries to load the bucket name from the :ref:`config <aws bucket config>`

    :returns: a string with the bucket name or ``None``
    """
    return any_of(
        conf.get('dao', 's3', 'bucket_name', fallback=None),
        conf.get('aws', 's3', 'default_bucket_name', fallback=None),
    )


def bucket(name=None):
    """auto-loads a session :py:func:`~python_clinic.aws.resource`
    :returns: a :py:class:`boto3.Bucket`
    """
    if not name:
        name = determine_default_bucket_name()

    if name is None:
        raise conf.ConfigKeyNotFound('bucket_name', 'dao.s3')

    b = resource('s3').Bucket(name)
    b.load()
    return b


class AwsConfigParser(ConfigParser):
    """Subclass of :py:class:`~configparser.ConfigParser` with a mechanism
    to prevent overwriting existing config.

    This is part of the self-configuration feature that has a
    substantial side-effect in the host machine.

    The *magic behavior* provided by this component can be tricky, so
    better be safe than sorry.
    """
    def __init__(self, path, load=False):
        super(AwsConfigParser, self).__init__()
        path = pathlib.Path(path).expanduser().absolute()
        self._aws_file_path = path

        if load:
            self.load()

    @property
    def path(self):
        return self._aws_file_path

    def load(self):
        """Loads the existing config into this config parser instance"""
        if not self.path.is_file():
            return self

        self.read(self.path)
        return self

    def save(self, force=False):
        """dump the current data in the disk"""
        if self.path.is_file() and not force:
            return False

        with io.open(self.path, 'w') as stream:
            self.write(stream)

        return True


class AwsConfig(object):
    """Manages the `config files <https://docs.aws.amazon.com/cli/latest/reference/configure/index.html#configure>`_ usually under ``~/.aws/``
    """
    def __init__(self, config_path='~/.aws/config', credentials_path='~/.aws/credentials'):
        self.config = AwsConfigParser(config_path).load()
        self.credentials = AwsConfigParser(credentials_path).load()

    def write_profile(self):
        for profile_name, profile_config in conf.get_dict('aws', 'profile').items():
            if profile_name in self.config:
                continue

            if not profile_config:
                continue

            if profile_config and not isinstance(profile_config, dict):
                msg = 'the key aws.profile.{} should be a dict, got {}'
                raise PythonClinicConfigError(msg.format(profile_name, profile_config))

            self.config[profile_name] = dict(profile_config or {})
            logger.info('adding profile %s to ~/.aws/config', profile_name)

        self.config.save()

    def write_credentials(self):
        for profile_name, profile_credentials in conf.get_dict('aws', 'credentials').items():
            if profile_name in self.credentials:
                continue

            self.credentials[profile_name] = dict(profile_credentials)
            logger.info('adding credentials for profile %s to ~/.aws/credentials', profile_name)

        self.credentials.save()


def update_and_write_config_to_home():
    """takes the aws config from PYTHON_CLINIC_CONF_PATH and safely writes to ~/.aws/config.

    .. note:: **Any existing configs are preserved.** Existing values are never overwritten
    """
    manager = AwsConfig()
    try:
        manager.write_profile()
        logger.info('updated ~/.aws/config')

    except Exception as e:
        logger.warning('could not write profile to ~/.aws/config: %s', e)

    try:
        manager.write_credentials()
        logger.info('updated ~/.aws/credentials')
    except Exception as e:
        logger.warning('could not write credentials to ~/.aws/credentials: %s', e)


class PythonClinicConfigError(RuntimeError):
    pass
