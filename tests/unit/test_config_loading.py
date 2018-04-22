# -*- coding: utf-8 -*-
from pathlib import PosixPath
from os.path import expanduser
from mock import patch

from python_clinic import conf
from python_clinic.conf import current_path
from python_clinic.conf import determine_config_path
from python_clinic.conf import get_lookup_paths
# from python_clinic.conf import InvalidDictConfigError
from python_clinic.conf import NoConfigFilesFound
from python_clinic.conf import load


@patch('python_clinic.conf.os')
def test_current_path(os):
    ("conf.current_path() should join parts to the current working dir")

    # Given that os.getcwd() returns a POSIX path
    os.getcwd.return_value = '/home/python-clinic'

    # When I call current_path()
    result = current_path('example', 'config.yml')

    # Then it should return a full path
    result.should.equal('/home/python-clinic/example/config.yml')


@patch('python_clinic.conf.os')
@patch('python_clinic.conf.current_path')
def test_get_lookup_paths(current_path, os):
    ("conf.get_lookup_paths() should join parts to the current working dir")
    current_path.return_value = './python-clinic.yml'
    os.getenv.return_value = '/srv/python-clinic/conf.yml'

    paths = get_lookup_paths()

    paths.should.equal([
        '/srv/python-clinic/conf.yml',
        '/etc/python-clinic.yaml',
        expanduser('~/.python-clinic.yaml'),
        './python-clinic.yml'
    ])


@patch('python_clinic.conf.get_lookup_paths')
@patch('python_clinic.conf.isfile')
@patch('python_clinic.conf.relpath')
def test_determine_config_path(relpath, isfile, get_lookup_paths):
    ('conf.determine_config_path() should return a relative path')

    isfile.side_effect = lambda x: x == '/etc/foo.yml'

    relpath.side_effect = lambda x: "./relative/to/{}".format(x.lstrip('/'))

    get_lookup_paths.return_value = [
        '/foo/bar.yml',
        '/etc/foo.yml',
    ]

    result = determine_config_path()
    result.should.equal(PosixPath('./relative/to/etc/foo.yml'))


@patch('python_clinic.conf.get_lookup_paths')
@patch('python_clinic.conf.isfile')
@patch('python_clinic.conf.relpath')
def test_determine_config_path_invalid(relpath, isfile, get_lookup_paths):
    ('conf.determine_config_path() should raise '
     'NoConfigFilesFound if none of the indicated files exist.')

    isfile.return_value = False

    get_lookup_paths.return_value = [
        '/foo/bar.yml',
        '/etc/foo.yml',
    ]

    determine_config_path.when.called_with().should.have.raised(
        NoConfigFilesFound,
        "no config was found in the paths: ['/foo/bar.yml', '/etc/foo.yml']"
    )


@patch('python_clinic.conf.io')
@patch('python_clinic.conf.isfile')
@patch('python_clinic.conf.yaml')
@patch('python_clinic.conf.determine_config_path')
def test_load(determine_config_path, yaml, isfile, io):
    "conf.load() should load a YAML from the pre-determined path"

    # Given that the file exists
    isfile.return_value = True

    # And yaml.load() returns a dict
    yaml.load.return_value = {
        'I': 'am',
        'the': 'config',
    }
    # And determine_config_path() returns a path
    determine_config_path.return_value = '/home/python-clinic/config.yml'

    # When I call conf.load()
    result = load()

    # Then it should return the yaml-loaded config
    result.should.equal({
        'I': 'am',
        'pythonclinic_config_dir': '/home/python-clinic',
        'the': 'config',
    })


@patch('python_clinic.conf.io')
@patch('python_clinic.conf.isfile')
@patch('python_clinic.conf.yaml')
@patch('python_clinic.conf.determine_config_path')
def test_load_throws(determine_config_path, yaml, isfile, io):
    ("conf.load(throw=True) should raise an IOError exception "
     "if yaml config file does not exist")

    # Given that the file does not exist
    isfile.return_value = False

    # And determine_config_path() returns a path
    determine_config_path.return_value = '/home/python-clinic/config.yml'

    # When I call conf.load(throw=True)
    after_called = load.when.called_with(throw=True)
    # Then it should raise IOError
    after_called.should.have.raised(
        IOError,
        'yaml config file does not exist: /home/python-clinic/config.yml',
    )


@patch('python_clinic.conf.io')
@patch('python_clinic.conf.isfile')
@patch('python_clinic.conf.yaml')
@patch('python_clinic.conf.determine_config_path')
def test_load_graceful_error(determine_config_path, yaml, isfile, io):
    "conf.load(throw=False) should return"

    # Given that the file does not exist
    isfile.return_value = False

    # And determine_config_path() returns a path
    determine_config_path.return_value = '/home/python-clinic/config.yml'

    # When I call conf.load(throw=False)
    result = load(throw=False)

    # Then it should return an empty dictionary
    result.should.equal({})


@patch('python_clinic.conf.load')
def test_get(load):
    "conf.get() should load the config and return a key from it"

    # Given that conf.load() is mocked
    load.return_value = {
        'postgresql': {
            'credentials': {
                'python-clinic': {
                    'username': 'guido'
                }
            }
        }
    }
    # When I call conf.get() on an existing key
    result = conf.get('postgresql', 'credentials', 'python-clinic', 'username')

    # Then it should return the expected value
    result.should.equal('guido')


@patch('python_clinic.conf.load')
def test_get_fallback(load):
    "conf.get() should use a fallback if the key was not found"

    # Given that conf.load() is mocked to have a None children
    load.return_value = {
        'root': {
            'child1': {}
        }
    }
    # When I call conf.get() on an existing key
    result = conf.get('root', 'child1', 'child2', 'child3', fallback='chuck-norris')

    # Then it should return the expected value
    result.should.equal('chuck-norris')


@patch('python_clinic.conf.load')
def test_get_not_dict(load):
    "conf.get() should fallback to empty dict by default"

    # Given that conf.load() is mocked to have a None children
    load.return_value = {
        'root': {
            'child1': None
        }
    }
    # When I call conf.get() when a one of the middle nodes is not a dict
    result = conf.get('root', 'child1', 'child2', 'child3')

    # Then it should have raised InvalidDictConfigError
    result.should.be.none
