from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from common import _rabbitmq_modules
from backend import _booking_modules


class Command(BaseCommand):
    help = "RabbitMq - Read Queue"

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            nargs='?',
            type=str,
            default='localhost'
        )

        parser.add_argument(
            '--queue',
            nargs='?',
            type=str,
            default='booking'
        )

    def display_host(self, rabbit_host):
        self.stdout.write(
            self.style.WARNING(f"Connecting to: {rabbit_host}")
        )

    def display_queue(self, rabbit_queue):
        self.stdout.write(
            self.style.WARNING(f"Reading From Queue: {rabbit_queue}")
        )

    def start_processing_queue(self, body):
        self.stdout.write(
            self.style.WARNING(f" [x] Received {body}")
        )
        # Process content
        if _rabbitmq_modules.RABBIT_MQ_INSTRUCTION_CACHE_UNITS in str(body):
            if _rabbitmq_modules.RABBIT_MQ_INSTRUCTION_CACHE_UNITS == str(body, encoding="utf-8"):
                _booking_modules.load_and_cache_units_details()

    def queue_on_standby(self):
        self.stdout.write(
            self.style.SUCCESS(' [*] Waiting for messages. To exit press CTRL+C')
        )

    def shutdown_queue(self):
        self.stdout.write(
            self.style.NOTICE('Shutting down...')
        )

    def handle(self, *args, **options):
        rabbit_queue = options["queue"]
        rabbit_host = options["host"]

        ''' DEBUG Refresh '''
        if settings.DEBUG:
            _booking_modules.load_and_cache_units_details()

        _rabbitmq_modules.read_from_rabbit_queue(
            self.display_host,
            self.display_queue,
            self.start_processing_queue,
            self.queue_on_standby,
            self.shutdown_queue,
            rabbit_queue,
            rabbit_host
        )
