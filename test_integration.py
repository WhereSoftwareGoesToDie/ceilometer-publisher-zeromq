from ceilometer import sample
from ceilometer_publisher_zeromq import queue
from urlparse import SplitResult
import os
import sys
import zmq

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
    #Setup connection
    context = zmq.Context()
    socket  = context.socket(zmq.REP)
    socket.bind("tcp://127.0.0.1:8282")
    #Use the publihser to publish a single message
    new_pid = os.fork()
    if new_pid == 0:
        queue.QueuePublisher(
            SplitResult(scheme = 'rabbitmq', netloc='', path='', query='', fragment='')
        ).publish_samples(None, [stub_sample()])
        os._exit(0)
    else:
        #Grab and check the message is as we expect
        a = socket.recv_json()
        socket.send("")
        a.pop('id', None)
        assert a == stub_expected()

if __name__ == '__main__':
    sys.exit(main())
