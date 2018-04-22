# -*- coding: utf-8 -*-
import os
import uuid
import pathlib

from jsonschema import ValidationError

from flask import Flask

from flask import url_for
from flask import render_template
from flask_cors import CORS

from flask_restplus import Api
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.exceptions import BadRequest

from python_clinic import aws
from python_clinic import conf
from python_clinic import logs
from python_clinic.dao import json
from python_clinic.web.schemas import json_response
from python_clinic.dao import FileStorage
from python_clinic.dao import S3Storage
from python_clinic.version import version
from python_clinic.web.logs import logger
from python_clinic.web.controllers import ControllerException


web_path = pathlib.Path(__file__).parent
ui_path = web_path.joinpath('ui')
ui_template_path = ui_path.joinpath('templates')
ui_static_path = ui_path.joinpath('admin-app/build/static')


class ApplicationContainer(Flask):
    """A subclass of :py:class:`~flask.Flask` with extended features for our service configuration.

    All RESTful endpoints are defined within an instance of this.


    Here is how you can add new endpoints:

    .. code:: python

       server = ApplicationContainer()
       namespace = namespace = api.namespace('account', description='User Account Operations')

       @namespace.route('/options')
       class ShipmentOptions(Resource):
           def get(self):
               users = get_user_list_from_some_controller()
               return list(users)

    """
    def __init__(self, *args, **params):
        params['static_folder'] = str(ui_static_path)
        params['template_folder'] = str(ui_template_path)
        super(ApplicationContainer, self).__init__('python_clinic.web', *args, **params)

        self.version = version
        self.dao = None
        self.wsgi_app = ProxyFix(self.wsgi_app)
        # we must register the url "/" before instantiating an Api, or else it will replace with its own
        self.add_url_rule('/', 'index', self.serve_app)
        self.api = Api(self, doc='/api/')
        self.cors = CORS(self, resources="/*")
        # self-(re)configuration
        self.auto_configure()

    def auto_configure(self):
        """(re) configures the application container server
        """
        varname = '__PYTHON_CLINIC_DISABLE_AUTOCONFIG'
        flag = os.getenv(varname)
        if flag:
            msg = (
                'Skipping auto configuration because the '
                'environment variable %s is set to "%s". '
                'You better be running a test :)'
            )
            logger.critical(msg, varname, flag)
            return

        logger.info('initializing application container')
        self.configure_web()
        self.configure_aws()
        self.configure_dao()
        self.configure_timezone()

    def configure_web(self):
        """configures stuff required by Flask, this must always be called
        before any of the ``self.configure_*`` methods.
        """
        self.configure_logging()

        self.config.update(conf.get('app', fallback={}))
        self.server_name = conf.get('app', 'SERVER_NAME', fallback='localhost')
        if not self.config.get('BASE_URL'):
            self.config['BASE_URL'] = 'http://{}'.format(self.server_name)

        # SERVER_NAME hack
        # https://stackoverflow.com/questions/24437248/unexplainable-flask-404-errors
        self.config['SERVER_NAME'] = None

        logger.info('base_url: %s', self.config['BASE_URL'])

    def configure_logging(self):
        """sets the log level of all loggers"""
        level = logs.determine_log_level()
        logs.set_level(level)

    def configure_aws(self):
        """this method *can* have a side-effect in its host: write to ``~/.aws/{config,credentials}``
        To disable this read the documentation about :ref:`self_configuration`
        """
        should_auto_write = bool(conf.get('aws', 'create_missing_config'))
        if should_auto_write is True:
            aws.update_and_write_config_to_home()

    def configure_dao(self):
        """Tries to use the first available DAO backend, the lookup has the
        following priority order:

        1. :py:class:`~python_clinic.dao.s3.S3Storage`
        2. :py:class:`~python_clinic.dao.files.FileStorage`
        """
        for DaoBackend in (S3Storage, FileStorage):
            name = DaoBackend.__name__
            if not DaoBackend.is_available():
                logger.debug('DAO backend %s is not available in this host', name)
                continue

            self.dao = DaoBackend()
            logger.info('using DAO backend: %s', name)
            return

    def configure_timezone(self):
        """this method doesn't really configure anything as much as it warns
        developers when the timezone is not configured. Which can help
        mitigate integration problems sooner.
        """
        timezone = conf.get('app', 'TIMEZONE')
        if not timezone:
            logger.warning('timezone is not configured')
        else:
            logger.info('service is on the %s timezone', timezone)

    @property
    def base_url(self):
        url = self.config.get('BASE_URL')
        if not url:
            raise RuntimeError('missing app.BASE_URL from yaml config')

        return url

    def make_full_url(self, path):
        """takes a url path string and returns a full url based on the
        server's base_url.

        :ref:`server urls`
        """
        return '/'.join([self.base_url.rstrip('/'), path.lstrip('/')])

    def full_url_for(self, *args, **kw):
        """wrapper around :py:func:`flask.url_for` that ensures the full url based on the :ref:`server urls` config
        """
        return self.make_full_url(url_for(*args, **kw))

    def serve_app(self):
        """built-in handler for the root route ``/``

        This is defined as a method of the application container
        because it must be registered before instantiating a
        :py:class:`flask_restplus.Api`, which has to happen before
        importing other modules.

        :returns: a string with the html template for the web app (React App)
        """
        config = dict([(key, value) for key, value in self.config.items() if isinstance(value, (str, bytes, int, float, bool))])
        context = {
            'json': json,
            'config': config,
            'base_url': self.make_full_url(''),
            'seed': str(uuid.uuid4()),
        }
        return render_template('react-app.html', **context)

    def run(self, *args, **kw):
        """Runs the application container in developer mode, auto reloads the
        code if any relevant files are changed.

        .. warning:: This method should never be called in a production setting
        """
        extra_files = kw.pop('extra_files', [])
        extra_files.append(conf.determine_config_path())
        extra_files.extend(map(str, ui_template_path.glob('**/*.html')))
        extra_files.extend(map(str, ui_static_path.glob('**/*.js')))
        extra_files.extend(map(str, ui_static_path.glob('**/*.css')))
        extra_files.extend(map(str, web_path.glob('schemas/**/*.json')))
        kw['extra_files'] = extra_files
        return super(ApplicationContainer, self).run(*args, **kw)

    def handle_exception(self, error):
        """default exception handler that captures any server errors and logs
        them appropriately
        """
        status_code = 500
        data = {
            'message': str(error),
        }

        if isinstance(error, (BadRequest, ValidationError)):
            status_code = 400
        elif isinstance(error, ControllerException):
            status_code = error.status_code
            data = error.to_dict()

        self.logger.exception('unhandled server error: %s', error)

        return json_response(data, status_code)


application = ApplicationContainer()


@application.errorhandler(ControllerException)
def handle_controller_exception(error):
    status_code = error.status_code
    data = error.to_dict()
    return json_response(data, status_code)


api = application.api
