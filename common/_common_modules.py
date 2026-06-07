import traceback, json, sentry_sdk
from datetime import date, datetime


'''
Cached Units Key Value
'''
CACHED_UNITS_KEY_GLOBAL = 'cached_units'


'''
Loggers
'''
def logger_error(msg):
    try:
        print('\n............................')
        print(msg)
        print(traceback.format_exc())
        print('............................\n')
        # sentry_sdk.capture_message(msg, level="error")
        return True
    except Exception as e:
        print(e)
    return False


def logger_info(msg):
    print('\n............................')
    print(msg)
    print('............................\n')
    return True


'''
Visual Aid
'''
def improve_log_readability():
    print('\n............................')
    return True


'''
Health Endpoint
'''
def health():
    return {
        'status': 'up',
        'current_time': datetime.now()
    }


'''
Decode Content
'''
def format_request_parameters(payload, payload_type):
    try:
        logger_info(type(payload))
        if payload_type == 'json':
            payload = json.loads(payload.decode('utf-8'))
            logger_info(type(payload))
    except Exception as e:
        logger_error(e)
    return payload
