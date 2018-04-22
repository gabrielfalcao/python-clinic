# -*- coding: utf-8 -*-
from sure import anything

from python_clinic.web.schemas import json

from tests.functional.scenarios import api_client
from tests.functional.scenarios import apidoc_title
from tests.functional.scenarios import apidoc_description


@api_client
@apidoc_title("Create a project")
@apidoc_description("Requires ``name`` and ``author``")
def test_create_project(context):
    ('POST /api/v1/projects should return 201')

    response = context.http.post(
        '/api/v1/projects',
        data=json.dumps(dict(
            name='MY AwEsome PROject 1',
            author='norrischuck',
        )),
        content_type='application/json'
    )

    # Then it returns 201 - application/json
    response.status_code.should.equal(201)
    response.headers.should.have.key('Content-Type').being.equal(
        'application/json'
    )

    # And the response should match my configured shipping options
    data = json.loads(response.data)
    data.should.equal({
        "uuid": anything,
        "name": 'my-awesome-project-1',
        "author": "norrischuck",
        "web_page_url": "https://python.clinic/projects/my-awesome-project-1"
    })


@api_client
@apidoc_title("Edit a project")
@apidoc_description("Requires ``name`` and ``author``")
def test_edit_project(context):
    ('PUT /api/v1/project/uuid should return 200')

    response = context.http.put(
        '/api/v1/project/some-uuid',
        data=json.dumps(dict(
            name='MY AwEsome PROject 2',
            author='norrischuck',
        )),
        content_type='application/json'
    )

    # Then it returns 201 - application/json
    response.status_code.should.equal(200)
    response.headers.should.have.key('Content-Type').being.equal(
        'application/json'
    )

    # And the response should match my configured shipping options
    data = json.loads(response.data)
    data.should.equal({
        "uuid": anything,
        "name": 'my-awesome-project-2',
        "author": "norrischuck",
        "web_page_url": "https://python.clinic/projects/my-awesome-project-2"
    })


@api_client
@apidoc_title("Delete a project")
@apidoc_description("Requires ``name`` and ``author``")
def test_delete_project(context):
    ('DELETE /api/v1/project/uuid should return 200')

    response = context.http.delete(
        '/api/v1/project/some-uuid',
        content_type='application/json'
    )

    # Then it returns 201 - application/json
    response.status_code.should.equal(200)
    response.headers.should.have.key('Content-Type').being.equal(
        'application/json'
    )

    # And the response should match my configured shipping options
    data = json.loads(response.data)
    data.should.equal({
        "uuid": 'some-uuid',
    })
