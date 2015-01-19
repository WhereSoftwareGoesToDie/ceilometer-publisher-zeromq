from ceilometer import sample
from ceilometer_publisher_rabbitmq import queue
from urlparse import SplitResult
import json
import kombu
import sys

def stub_sample():
    return sample.Sample(
        "stub_name",
        "gauge",
        "MB",
        "14",
        "larry-id",
        "larrys-project-id",
        "larrys-box-id",
        "antediluvian",
        {"redundant-data": "data"},
    )

def stub_expected():
    return {
        "name": "stub_name",
        "type": "gauge",
        "unit": "MB",
        "volume": "14",
        "user_id": "larry-id",
        "project_id": "larrys-project-id",
        "resource_id": "larrys-box-id",
        "timestamp": "antediluvian",
        "resource_metadata": {
            "redundant-data": "data"
        },
        "source": "openstack",
    }

def main(argv=None):
    #Overwrite options
    options=queue.cfg.CONF
    options.publisher_rabbit_host='localhost'
    options.publisher_rabbit_user='guest'
    options.publisher_rabbit_password='guest'
    options.publisher_exchange='publisher-test-exchange'
    options.publisher_queue='publisher-test-queue'
    #Setup connection
    connection = kombu.Connection(
        hostname     = options.publisher_rabbit_host,
        userid       = options.publisher_rabbit_user,
        password     = options.publisher_rabbit_password,
        virtual_host = options.publisher_rabbit_virtual_host,
        port         = options.publisher_rabbit_port,
    )
    connection.connect()
    #Use the publihser to publish a single message
    queue.QueuePublisher(
        SplitResult(scheme='rabbitmq', netloc='', path='', query='', fragment='')
    ).publish_samples(None, [stub_sample()])
    #Grab and check the message is as we expect
    test_queue = connection.SimpleQueue(options.publisher_queue)
    message = test_queue.get(block=True, timeout=1)
    if message:
        message.ack()
        cleaned = json.loads(message.payload)
        cleaned.pop('id', None)
        test_queue.close()
        assert cleaned == stub_expected()
    else:
        print 'No messaged returned'
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
