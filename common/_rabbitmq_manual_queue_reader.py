#!/usr/bin/env python
import sys, os
# import _rabbitmq_modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common import _rabbitmq_modules


def shutdown_queue():
    print('Shutting down...')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


def display_host(rabbit_host):
    print(f"Connecting to: {rabbit_host}")


def display_queue(rabbit_queue):
    print(f"Reading From Queue: {rabbit_queue}")


def start_processing_queue(body):
    print(f" [x] Received {body}")


def queue_on_standby():
    print(' [*] Waiting for messages. To exit press CTRL+C')


def main():
    _rabbitmq_modules.read_from_rabbit_queue(
        display_host,
        display_queue,
        start_processing_queue,
        queue_on_standby,
        shutdown_queue
    )


if __name__ == '__main__':
    main()
