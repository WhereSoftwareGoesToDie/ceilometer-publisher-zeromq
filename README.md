ceilometer-publisher-zeromq
=============================

ZeroMQ Publisher for Ceilometer.


Goals
-----

The traditional Ceilometer publisher, which sends data to MySQL or MongoDB did
not suit our needs, and our attempt at writing directly to libmarquise
spoolfiles didn't have the desired performance characteristics.

This publisher writes to a collector via ZeroMQ as simply and quickly as possible,
leaving subsequent processing to a separate process.


Data flow
---------

1. Openstack produces a JSON message blob
2. Enters the Ceilometer pipeline via a ceilometer agent
3. ceilometer-publisher-zeromq sends the JSON to a collector over a ZeroMQ Connection
4. vaultaire-collector-ceilometer performs any necessary processing,
   then writes the output to a spoolfile via marquise
5. Spoolfiles are read and shipped to Vaultaire by a marquised process.


Installation + Deployment
-------------------------

1. Install from source.
    ```
    git clone git@github.com:anchor/ceilometer-publisher-zeromq.git
    cd ceilometer-publisher-zeromq
    python setup.py install
    ```

2. Add *zeromq://* to the publishers in your `pipeline.yaml`.
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
              - zeromq://
    ```

3. Add the credentials + options you require to your `ceilometer.conf`
   (This also in `/etc/ceilometer/` by default).

   Partial example `ceilometer.conf`:

    ```
    [DEFAULT]
    publisher_zeromq_host = 127.0.0.1
    publisher_zeromq_port = 8282
    ```

4. Restart the central and notification ceilometer agents (`ceilometer-acentral + ceilometer-anotification`)
