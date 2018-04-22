Delete a project
----------------

.. _test_delete_project:

.. http:delete:: /api/v1/project/some-uuid

   Requires ``name`` and ``author``

   **Example request**:

   .. sourcecode:: http

      POST /api/v1/project/some-uuid HTTP/1.1
      Host: localhost
      User-Agent: werkzeug/0.14.1
      Host: localhost
      Content-Type: application/json

      


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK HTTP/1.1
      Content-type: application/json
      Content-length: 21
      Access-control-allow-origin: *

      {
        "uuid": "some-uuid"
      }