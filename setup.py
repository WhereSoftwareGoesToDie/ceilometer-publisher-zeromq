import os
import uuid
from setuptools import setup
from pip.req import parse_requirements

# Utility function to read the README file.  Used for the long_description.
# It's nice, because now 1) we have a top level README file and 2) it's easier
# to type in the README file than to put a raw string in below.
def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name="ceilometer-publisher-rabbitmq",
    version="0.0.6",
    description="A publisher plugin for Ceilometer that outputs to RabbitMQ",
    author="Oswyn Brent",
    author_email="oswyn.brent@anchor.com.au",
    maintainer_email="engineering@anchor.net.au",
    url="https://github.com/anchor/ceilometer-publisher-rabbitmq",
    zip_safe=False,
    packages=[
        "ceilometer_publisher_rabbitmq",
    ],
    package_data={
        "ceilometer_publisher_rabbitmq" : ["README.md"],
    },
    long_description=read("README"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    entry_points = {
        "ceilometer.publisher": [
            "rabbitmq = ceilometer_publisher_rabbitmq.queue:QueuePublisher",
        ],
    },
    install_requires=[str(req.req) for req in parse_requirements("requirements.txt", session=uuid.uuid1())],
    include_package_data=True
)
