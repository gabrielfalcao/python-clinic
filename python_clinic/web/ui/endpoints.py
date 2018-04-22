# -*- coding: utf-8 -*-
import io
import uuid
from flask import render_template
from flask import send_from_directory
from pathlib import Path
from python_clinic.dao import json
from python_clinic.logs import get_logger
from python_clinic.version import version
from python_clinic.web.schemas import json_response
from python_clinic.web.server import application

from .controllers import WebUIController


logger = get_logger(__name__)


controller = WebUIController(application)


ui_path = Path(__file__).parent                                    # ./
not_found_png = io.open(ui_path.joinpath('404.png'), 'rb').read()  # ./404.png

web_path = ui_path.parent                                          # ../
root_module_path = web_path.parent                                 # ../../
docs_path = root_module_path.joinpath('docs')                      # ../../docs/
react_app_path = root_module_path.joinpath('frontend/admin-app')   # ../../frontend/admin-app/
static_path = react_app_path.joinpath('build/static')              # ../../frontend/admin-app/build/static


@application.route('/health')
def healthcheck():
    data = {
        'name': 'Python Clinic',
        'version': version,
    }
    return json_response(data)


@application.route('/admin')
@application.route('/app')
def react_app(*args, **kw):
    config = dict([(key, value) for key, value in application.config.items() if isinstance(value, (str, bytes, int, float, bool))])
    context = {
        'json': json,
        'config': config,
        'base_url': application.make_full_url(''),
        'seed': str(uuid.uuid4()),
    }
    return render_template('react-app.html', **context)


@application.route('/app.js')
def admin_app_js():
    return send_from_directory(
        str(static_path.joinpath('js')),
        'python-clinic-webapp.js',
    )


@application.route('/service-worker.js')
def service_worker_js():
    return send_from_directory(
        str(react_app_path),
        'service-worker.js',
    )


@application.route('/app.css')
def admin_app_css():
    return send_from_directory(
        str(static_path.joinpath('css')),
        'python-clinic-webapp.css',
    )


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(
        str(static_path),
        'favicon.ico',
    )


@application.route('/manifest.json')
def manifest():
    return send_from_directory(
        str(static_path),
        'manifest.json',
    )


@application.route('/logo.png')
def logo_png():
    return send_from_directory(
        str(react_app_path.joinpath('src/python-clinic')),
        'logo.png',
    )


def serve_docs(path='index.html'):
    return send_from_directory(str(docs_path), path)


@application.route('/docs')
def docs_index():
    return serve_docs()


@application.route('/docs/<path:path>')
def docs_path(path):
    return serve_docs(path)
