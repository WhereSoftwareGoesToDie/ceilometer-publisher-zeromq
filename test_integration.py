from ceilometer import publisher, sample
from ceilometer_publisher_rabbitmq import queue
from pprint import pprint
from urlparse import SplitResult
import pika
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

def main(argv=None):
    queue.cfg.CONF.publisher_rabbit_host='localhost'
    queue.cfg.CONF.publisher_rabbit_user='guest'
    queue.cfg.CONF.publisher_rabbit_password='guest'
    queue.cfg.CONF.publisher_exchange='publisher-test-exchange'
    queue.cfg.CONF.publisher_queue='publisher-test-queue'
    queue.QueuePublisher(
        SplitResult(scheme='rabbitmq', netloc='', path='', query='', fragment='')
    ).publish_samples(None, [stub_sample()])

if __name__ == '__main__':
    sys.exit(main())
