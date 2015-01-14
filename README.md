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


Installation + Deployment
-------------------------

1. Install from source.
    ```
    git clone git@github.com:anchor/ceilometer-publisher-rabbitmq.git
    cd ceilometer-publisher-rabbitmq
    python setup.py install
    ```

2. Add "rabbitmq://" to the publishers in your `pipeline.yaml`.
   (This is by default in `/etc/ceilometer/`)

   Example `pipeline.yaml`:

    ```
    sources:
        - name: meter_source
          interval: 42
          meters:
              - "*"
          sinks:
              - meter_sink
    sinks:
        - name: meter_sink
          transformers:
          publishers:
              - rabbitmq://
    ```

3. Add the credentials + options you require to your `ceilometer.conf`
   (This also in `/etc/ceilometer/` by default).

   Partial example `ceilometer.conf`:

    ```
    [DEFAULT]
    publisher_exchange = "publisher-exchange"
    publisher_queue = "publisher-queue"
    publisher_rabbit_user = guest
    publisher_rabbit_password = guest
    publisher_rabbit_host = 127.0.0.1
    ```

4. Restart the central ceilometer agent (`ceilometer-acentral`)
