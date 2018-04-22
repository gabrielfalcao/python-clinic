# -*- coding: utf-8 -*-
import shutil
import httpretty
import python_clinic
from pathlib import Path
from sure import scenario

from python_clinic import aws
from python_clinic.util import DateEngine
from python_clinic import application
from python_clinic.dao import FileStorage
from python_clinic.dao import S3Storage

from tests.functional.httpdomain_client import HttpDomainFlaskClient
from tests.functional.httpdomain_client import apidoc_title  # noqa
from tests.functional.httpdomain_client import apidoc_description  # noqa


datetime = DateEngine()

dao_path = Path(__file__).parent.joinpath('_state')
documentation_path = Path(python_clinic.__file__).parent.parent.joinpath('docs/source/api/v1')


def create_controller(ControllerClass):
    return ControllerClass(application)


def relative_path(path):
    return str(path.absolute().relative_to(dao_path))


def file_tree(path, pattern='**/*'):
    return list(sorted(map(relative_path, path.glob('**/*'))))


def s3_tree():
    bucket = aws.bucket()
    return [o.key for o in bucket.objects.all()]


def prepare_app_client(context):
    httpretty.reset()
    context.application = application
    context.http = HttpDomainFlaskClient.from_app(
        application,
        documentation_path=documentation_path
    )
    context.dao = application.dao
    context.controller = create_controller
    if context.dao.path.is_dir():
        shutil.rmtree(context.dao.path, ignore_errors=True)


api_client = scenario(prepare_app_client)


def prepare_file_dao(context):
    context.path = dao_path
    if dao_path.is_dir():
        shutil.rmtree(dao_path, ignore_errors=True)

    context.dao = FileStorage(root_path=dao_path)


def prepare_s3_dao(context):
    context.path = dao_path
    if dao_path.is_dir():
        shutil.rmtree(dao_path, ignore_errors=True)

    context.dao = S3Storage()
    # create bucket
    response = context.dao.bucket.create()
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200, 'failed to create bucket for s3 dao'


def cleanup_s3_dao(context):
    pass


def ensure_test_aws_credentials(context):
    aws.update_and_write_config_to_home()


with_file_dao = scenario([prepare_file_dao])

with_s3_dao = scenario([ensure_test_aws_credentials, prepare_s3_dao], [cleanup_s3_dao])
