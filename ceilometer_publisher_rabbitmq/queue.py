from ceilometer import publisher
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from oslo.config import cfg
import json
import pika

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
        credentials = pika.credentials.PlainCredentials(
            username = cfg.CONF.publisher_rabbit_user,
            password = cfg.CONF.publisher_rabbit_password,
            erase_on_connect = True,
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=cfg.CONF.publisher_rabbit_host,
                port=cfg.CONF.publisher_rabbit_port,
                virtual_host=cfg.CONF.publisher_rabbit_virtual_host,
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.exchange = cfg.CONF.publisher_exchange
        queue = cfg.CONF.publisher_queue
        self.channel.exchange_declare(exchange=self.exchange,
                                      type='fanout')
        self.channel.queue_declare(queue=queue,
                                   durable=True, auto_delete=False)
        self.channel.queue_bind(queue=queue,
                                exchange=self.exchange)

    def publish_samples(self, context, samples):
        """
        Converts each sample into a string of JSON and publishes it the setup rabbit queue
        """
        for sample in samples:
            LOG.debug("Queue Publisher got sample")
            message = json.dumps(sample.as_dict())
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key='',
                                       body=message,
                                       mandatory=True)
            LOG.debug(_("Queue Publisher published %s to exchange %s") % (message, self.exchange))
