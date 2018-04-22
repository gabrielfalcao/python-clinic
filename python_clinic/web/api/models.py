# -*- coding: utf-8 -*-
from python_clinic.helpers import fake
from python_clinic.web.server import api
from python_clinic.web.schemas import from_file, schema_parser


class requests:
    class v1:
        project = schema_parser(
            from_file('api/v1/request/project.json'),
            default={
                "name": fake.project_name(),
                "author": 'python-clinic',
            }
        )


class responses:
    class v1:
        project = api.schema_model(
            'project',
            from_file('api/v1/response/project.json'),
        )
        error = api.schema_model(
            'error',
            from_file('api/v1/response/error.json'),
        )
