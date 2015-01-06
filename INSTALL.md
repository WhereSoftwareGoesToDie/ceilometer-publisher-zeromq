1. Install this package
2. Edit your pipeline config(`/etc/ceilometer/pipeline.yaml`), adding an extra publisher, it'll look something like this:
    ```
    sinks:
        - name: meter_sink
          transformers:
          publishers:
              - notifier://
              - rabbitmq://
    ```
3. Edit your Ceilometer config, adding credential directives as applicable for your system. Something like this, in the `[DEFAULT]` section:
    ```
    publisher_exchange = "hs-publisher-exchange"
    publisher_queue = "hs-publisher-queue"
    publisher_rabbit_user = guest
    publisher_rabbit_password = super$secure*passw0rd
    publisher_rabbit_host = 192.168.42.42
    ```
4. Restart any necessary daemons. If you're running devstack, it'll be all seven whose name starts with "ceilometer".
