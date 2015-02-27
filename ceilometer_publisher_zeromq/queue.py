from ceilometer import publisher
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from oslo.config import cfg
import json
import zmq

LOG = log.getLogger(__name__)

OPTS = [
    cfg.StrOpt('publisher_zeromq_host',
               default='localhost'),
    cfg.IntOpt('publisher_zeromq_port',
               default=8282),
]

cfg.CONF.register_opts(OPTS)

class QueuePublisher(publisher.PublisherBase):
    """Republishes all received samples to a collector via ZeroMQ"""

    def __init__(self, parsed_url):
        LOG.info("Queue Publisher starting up")
        super(QueuePublisher, self).__init__(parsed_url)
        self.context = None
        self.socket  = None
        self.connect()

    def reconnect(self):
        """Terminates existing context then reconnects to the collector"""
        self.socket.close()
        self.context.term()
        self.connect()

    def connect(self):
        """connects to the collector"""
        self.context = zmq.Context()
        self.socket  = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://%s:%d" % (cfg.CONF.publisher_zeromq_host, cfg.CONF.publisher_zeromq_port))

    def publish_sample(self, message):
        """Attempt to publish a single sample"""
        self.socket.send(message)
        events = self.socket.poll(1000)
        if events == 0:
            return False
        else:
            self.socket.recv()
            return True

    def publish_samples(self, context, samples):
        """
        Converts each sample into a string of JSON and publishes it the setup rabbit queue
        """
        for sample in samples:
            LOG.debug("Queue Publisher got sample")
            message = json.dumps(sample.as_dict())
            while not self.publish_sample(message):
                LOG.warning("Failed to publish message reconnecting")
                self.reconnect()
            LOG.debug(_("Queue Publisher published %s") % message)
