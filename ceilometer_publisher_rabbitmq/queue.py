from ceilometer import publisher
from oslo.config import cfg
import pika

OPTS = [
    cfg.StrOpt('rabbit_hosts'),
    cfg.StrOpt('rabbit_user'),
    cfg.StrOpt('rabbit_password',
               default='use_more_haskell_123'),
    cfg.StrOpt('publisher_queue',
               default='publisher-queue',
               help='The rabbit queue to bind the exchange to'),
    cfg.StrOpt('rabbit_exchange',
               default='publisher-exchange',
               help='The exchange to use for publishing samples')
]

cfg.CONF.register_opts(OPTS)

class QueuePublisher(publisher.PublisherBase):
    """Republishes all received samples to a rabbit queue"""

    def __init__(self, parsed_url):
        super(QueuePublisher, self).__init__(parsed_url)
        credentials = pika.credentials.PlainCredentials(username = cfg.CONF.rabbit_user,
                                                        password = cfg.CONF.rabbit_password,
                                                        erase_on_connect = True)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg.CONF.rabbit_hosts,
                                                                            port=5672,
                                                                            virtual_host='/',
                                                                            credentials=credentials))
        self.channel = self.connection.channel()
        self.exchange = cfg.CONF.rabbit_exchangengs['exchange']
        self.channel.exchange_declare(exchange=self.exchange)
        queue = cfg.CONF.publisher_queue
        self.channel.queue_declare(queue=queue)
        self.channel.queue_bind(queue=queue, exchange=self.exchange)

    def publish_samples(self, context, samples):
        """
        Converts each sample into a string of JSON and publishes it the setup rabbit queue
        """
        for sample in samples:
            message = str(sample.as_dict())
            self.channel.basic_publish(exchange=self.exchange,
                                       body=message)
