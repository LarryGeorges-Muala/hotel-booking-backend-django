import json, pika, sys, os
from . import _common_modules


'''
Rabbit - Details
'''
RABBIT_MQ_HOST = os.getenv('RABBIT_MQ_HOST', 'localhost')
RABBIT_MQ_QUEUE = "booking"
RABBIT_MQ_INSTRUCTION_CACHE_UNITS = "cache_units"


'''
Rabbit - Record
'''
def add_to_rabbit_queue(payload, payload_type=''):
    rabbit_queue = RABBIT_MQ_QUEUE
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_MQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(
            queue=rabbit_queue,
            durable=True,
            arguments={
                'x-queue-type': 'quorum'
            }
        )
        try:
            if payload_type == 'json':
                channel.basic_publish(
                    exchange='',
                    routing_key=rabbit_queue,
                    body=json.dumps(payload),
                    properties=pika.BasicProperties(content_type='application/json')
                )
            else:
                channel.basic_publish(
                    exchange='',
                    routing_key=rabbit_queue,
                    body=payload
                )
            _common_modules.logger_info(f" [x] Sent '{payload}'")
            connection.close()
            return True
        except Exception as e:
            _common_modules.logger_error(e)
            connection.close()
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Rabbit - Read and Process
'''
def read_from_rabbit_queue(
        display_host,
        display_queue,
        start_processing_queue,
        queue_on_standby,
        shutdown_queue,
        rabbit_queue=RABBIT_MQ_QUEUE,
        rabbit_host=RABBIT_MQ_HOST
    ):
    display_host(rabbit_host)
    display_queue(rabbit_queue)
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(rabbit_host)
        )
        try:
            channel = connection.channel()
            channel.queue_declare(
                queue=rabbit_queue,
                durable=True,
                arguments={
                    'x-queue-type': 'quorum'
                }
            )
            def callback(ch, method, properties, body):
                _common_modules.logger_info(
                    f'''
                    {type(body)}
                    '''
                )
                start_processing_queue(body) # Process content in this function

            channel.basic_consume(
                queue=rabbit_queue,
                on_message_callback=callback,
                auto_ack=True
            )
            queue_on_standby()
            channel.start_consuming()
        except KeyboardInterrupt:
            connection.close()
            shutdown_queue()

    except Exception as e:
        _common_modules.logger_error(e)
