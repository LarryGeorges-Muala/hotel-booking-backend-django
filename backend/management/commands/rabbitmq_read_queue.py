import pika, sys, os
from django.core.management.base import BaseCommand, CommandError


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

    def handle(self, *args, **options):
        try:
            rabbit_queue = options["queue"]
            rabbit_host = options["host"]

            self.stdout.write(
                self.style.WARNING(f"Reading From Queue: {rabbit_queue}")
            )
            self.stdout.write(
                self.style.WARNING(f"Connecting to: {rabbit_host}")
            )

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbit_host
                )
            )
            channel = connection.channel()

            channel.queue_declare(
                queue=rabbit_queue,
                durable=True,
                arguments={
                    'x-queue-type': 'quorum'
                }
            )

            def callback(ch, method, properties, body):
                self.stdout.write(
                    self.style.WARNING(f" [x] Received {body}")
                )

                # Add operation after retrieving from queue

            channel.basic_consume(
                queue=rabbit_queue,
                on_message_callback=callback,
                auto_ack=True
            )

            self.stdout.write(
                self.style.SUCCESS(' [*] Waiting for messages. To exit press CTRL+C')
            )
            channel.start_consuming()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.NOTICE('Shutting down...')
            )
        except Exception as e:
            raise CommandError(e)
