from ceilometer import publisher
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from oslo.config import cfg
import json
import zmq
from Queue import Queue, Empty
import threading

LOG = log.getLogger(__name__)

OPTS = [
    cfg.StrOpt('publisher_zeromq_host',
               default='localhost'),
    cfg.IntOpt('publisher_zeromq_port',
               default=8282),
]

cfg.CONF.register_opts(OPTS)

class ZeroMQPublisher(publisher.PublisherBase):
    """Republishes all received samples to a collector via ZeroMQ"""

    def __init__(self, parsed_url):
        LOG.info("ZeroMQ publisher starting up")
        self.lock = threading.Lock()
        super(ZeroMQPublisher, self).__init__(parsed_url)
        self.context = None
        self.socket  = None
        self.queue = Queue()
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

    def publish_everything(self):
        """Attempt to publish a single sample"""
        while not self.queue.empty():
            self.lock.acquire(blocking=True)
            try:
                message = self.queue.get(block=False)
                self.socket.send(message)
                events = self.socket.poll(1000)
                if events == 0:
                    self.queue.put(message)
                    LOG.debug("Publisher failed to publish %s, reconnecting" % message)
                    self.reconnect()
                else:
                    self.socket.recv()
                    LOG.debug("Publisher successfully published %s" % message)
            except Empty:
                #Queue is empty, publishing is finished
                pass
            finally:
                self.lock.release()

    def publish_samples(self, context, samples):
        """
        Converts each sample into a string of JSON and publishes it the setup rabbit queue
        """
        for sample in samples:
            LOG.debug("ZeroMQ publisher got sample")
            message = json.dumps(sample.as_dict())
            self.queue.put(message)
            LOG.debug(_("ZeroMQ publisher enqueued %s") % message)
        self.publish_everything()
