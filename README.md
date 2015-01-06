ceilometer-publisher-rabbitmq
=============================

RabbitMQ Publisher for Ceilometer.


Goals
-----

The traditional Ceilometer publisher, which sends data to MySQL or MongoDB did
not suit our needs, and our attempt at writing directly to libmarquise
spoolfiles didn't have the desired performance characteristics.

This publisher writes to a RabbitMQ exchange as simply and quickly as possible,
leaving collection and subsequent processing to a separate process.


Data flow
---------

1. Openstack produces a JSON message blob
2. Enters the Ceilometer pipeline either from a Telemetry (Ceilometer) or
   Compute (Nova?) node
3. Is published to the `rabbitmq` sink
4. JSON message blob is enqueued to RabbitMQ (this is also durable; desirable)
5. Reader process reads from the RabbitMQ exchange, performs any necessary
   processing, then writes the output to a spoolfile via libmarquise
6. Spoolfiles are read and shipped to Vaultaire by a marquised process.
