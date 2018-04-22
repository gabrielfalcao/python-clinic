# -*- coding: utf-8 -*-
from tests.functional.scenarios import api_client


@api_client
def test_docs_endpoint(context):
    ('GET /docs should return 200')

    # context.http.get('/docs').status_code.should.equal(200)
    # context.http.get('/docs/index.html').status_code.should.equal(200)
    # context.http.get('/docs/1nv4l1d.f1l3n4m3').status_code.should.equal(404)
