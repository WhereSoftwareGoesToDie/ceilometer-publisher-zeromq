from ceilometer import publisher
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from oslo.config import cfg
from time import sleep
import json
import kombu

LOG = log.getLogger(__name__)

OPTS = [
    cfg.StrOpt('publisher_rabbit_host'),
    cfg.StrOpt('publisher_rabbit_user'),
    cfg.StrOpt('publisher_rabbit_password'),
    cfg.IntOpt('publisher_rabbit_port',
               default=5672),
    cfg.StrOpt('publisher_rabbit_virtual_host',
               default='/'),
    cfg.StrOpt('publisher_exchange',
               default='publisher-exchange',
               help='The exchange to use for publishing samples'),
    cfg.StrOpt('publisher_queue',
               default='publisher-queue',
               help='The queue to use for publishing samples'),
]

cfg.CONF.register_opts(OPTS)

class QueuePublisher(publisher.PublisherBase):
    """Republishes all received samples to a rabbit queue"""

    def __init__(self, parsed_url):
        super(QueuePublisher, self).__init__(parsed_url)
        self.connection = None
        self.channel = None
        self.exchange = None
        self.reconnect()

    def reconnect(self):
        """(re)connects to the configured rabbit server"""
        self.connection = kombu.Connection(
            hostname     = cfg.CONF.publisher_rabbit_host,
            userid       = cfg.CONF.publisher_rabbit_user,
            password     = cfg.CONF.publisher_rabbit_password,
            virtual_host = cfg.CONF.publisher_rabbit_virtual_host,
            port         = cfg.CONF.publisher_rabbit_port,
        )
        self.connection.connect()
        self.channel = self.connection.channel()
        self.exchange = kombu.Exchange(
            name        = cfg.CONF.publisher_exchange,
            type        = 'fanout',
            channel     = self.channel,
            durable     = True,
            auto_delete = False,
        )
        self.exchange.declare()

        queue = kombu.Queue(
            name     = cfg.CONF.publisher_queue,
            exchange = self.exchange,
            channel  = self.channel,
        )
        queue.declare()

    def publish_sample(self, message):
        """Attempt to publish a single sample"""
        if self.connection.connected:
            self.exchange.publish(
                message = self.exchange.Message(message),
                routing_key='',
            )
            return True
        else:
            LOG.info("Tried publishing while disconnected, reconnecting.")
            return False

    def publish_samples(self, context, samples):
        """
        Converts each sample into a string of JSON and publishes it the setup rabbit queue
        """
        for sample in samples:
            LOG.debug("Queue Publisher got sample")
            message = json.dumps(sample.as_dict())
            while not self.publish_sample(message):
                LOG.warning("Failed to publish message, sleeping 3 seconds then reconnecting")
                sleep(3)
                self.reconnect()
            LOG.debug(_("Queue Publisher published %s to exchange %s") % (message, self.exchange))
