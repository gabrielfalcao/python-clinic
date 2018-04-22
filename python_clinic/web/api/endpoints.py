# -*- coding: utf-8 -*-
from flask_restplus import Resource

from python_clinic.web.server import api
from python_clinic.web.server import application
from python_clinic.web.schemas import JsonSchemaHttpPair
from python_clinic.logs import get_logger

from . import models
from .controllers import ProjectController


logger = get_logger(__name__)


api_v1 = api.namespace(
    'api_v1',
    description='Python Clinic API v1',
    path='/api/v1'
)


@api_v1.route('/projects')
class Projects(Resource):
    """Handles ``POST /api/v1/projects``

    - controller: :py:class:`~python_clinic.web.api.controllers.ProjectController`
    """

    controller = ProjectController(application)

    http = JsonSchemaHttpPair(
        request_file='api/v1/request/project.json',
        response_files={
            200: 'api/v1/response/project.json',
            400: 'api/v1/response/error.json',
        }
    )

    @api_v1.expect(models.requests.v1.project, validate=True)
    @api_v1.response(200, 'returns the project data', model=models.responses.v1.project)
    @api_v1.response(400, 'missing required fields', model=models.responses.v1.error)
    def post(self):
        data = self.http.request.parse()

        project = self.controller.create_project(**data)
        return self.http.response(project, 201)

    @api_v1.response(200, 'list projects', model=models.responses.v1.project, as_list=True)
    @api_v1.response(404, 'no projects found', model=models.responses.v1.error)
    def get(self):
        project = self.controller.list_projects()
        return self.http.response(project, 201)


@api_v1.route('/project/<uuid>')
class ManageProject(Resource):
    """Handles ``POST /api/v1/project/<uuid>``

    - controller: :py:class:`~python_clinic.web.api.controllers.ProjectController`
    """

    controller = ProjectController(application)

    http = JsonSchemaHttpPair(
        request_file='api/v1/request/project.json',
        response_files={
            200: 'api/v1/response/project.json',
            400: 'api/v1/response/error.json',
        }
    )

    @api_v1.expect(models.requests.v1.project, validate=True)
    @api_v1.response(200, 'returns the project data', model=models.responses.v1.project)
    @api_v1.response(400, 'invalid field data', model=models.responses.v1.error)
    @api_v1.response(404, 'project not found', model=models.responses.v1.error)
    def put(self, uuid):
        data = self.http.request.parse()
        project = self.controller.edit_project(uuid, **data)
        return self.http.response(project, 200)

    @api_v1.response(200, 'delete a project', model=models.responses.v1.project)
    @api_v1.response(404, 'project not found', model=models.responses.v1.error)
    def delete(self, uuid):
        project = self.controller.delete_project(uuid)
        return self.http.response(project, 200)

    @api_v1.response(200, 'retrieve project data', model=models.responses.v1.project)
    @api_v1.response(404, 'project not found', model=models.responses.v1.error)
    def get(self, uuid):
        project = self.controller.retrieve_project(uuid)
        return self.http.response(project, 200)
