Create a project
----------------

.. _test_create_project:

.. http:post:: /api/v1/projects

   Requires ``name`` and ``author``

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/projects HTTP/1.1
      Host: localhost
      User-Agent: werkzeug/0.14.1
      Host: localhost
      Content-Type: application/json
      Content-Length: 57

      {
        "name": "MY AwEsome PROject 1",
        "author": "norrischuck"
      }


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 201 CREATED HTTP/1.1
      Content-type: application/json
      Content-length: 176
      Access-control-allow-origin: *

      {
        "uuid": "afc866ce-e028-44d6-b15a-b7c07f093ace",
        "name": "my-awesome-project-1",
        "author": "norrischuck",
        "web_page_url": "https://python.clinic/projects/my-awesome-project-1"
      }