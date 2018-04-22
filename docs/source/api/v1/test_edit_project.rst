Edit a project
--------------

.. _test_edit_project:

.. http:put:: /api/v1/project/some-uuid

   Requires ``name`` and ``author``

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/project/some-uuid HTTP/1.1
      Host: localhost
      User-Agent: werkzeug/0.14.1
      Host: localhost
      Content-Type: application/json
      Content-Length: 57

      {
        "name": "MY AwEsome PROject 2",
        "author": "norrischuck"
      }


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK HTTP/1.1
      Content-type: application/json
      Content-length: 149
      Access-control-allow-origin: *

      {
        "uuid": "some-uuid",
        "name": "my-awesome-project-2",
        "web_page_url": "https://python.clinic/projects/my-awesome-project-2",
        "author": "norrischuck"
      }