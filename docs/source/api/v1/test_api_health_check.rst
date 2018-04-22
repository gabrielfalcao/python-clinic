Health-Check
------------

.. _test_api_health_check:

.. http:get:: /health

   Used as *ping path* in the `Elastic Load Balancer configuration
   <https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-healthchecks.html#health-check-configuration>`_.

   **Example request**:

   .. sourcecode:: http

      POST /health HTTP/1.1
      Host: localhost
      User-Agent: werkzeug/0.14.1
      Host: localhost

      


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK HTTP/1.1
      Content-type: application/json
      Content-length: 45
      Access-control-allow-origin: *

      {
        "name": "Python Clinic",
        "version": "1.0.0"
      }