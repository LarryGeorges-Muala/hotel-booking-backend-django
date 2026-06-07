import redis
from . import _common_modules


'''
Redis - Init
'''
def init_redis():
    return redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True
    )


'''
Redis Session - Create
'''
def create_redis_session(package_name, payload, set_expiration=True, expiration_parameters=(3600 * 24)):
    try:
        r = init_redis()
        try:
            # Save session
            _common_modules.logger_info(payload)
            r.hset(package_name, mapping=payload)
            # Check session
            user_session = r.hgetall(package_name)
            # Session expiration
            if set_expiration:
                r.expire(
                    package_name,
                    expiration_parameters
                )
            _common_modules.logger_info(
                f'''
                Redis created session '{package_name}' with expiration '{set_expiration}' of '{expiration_parameters}'
                {type(user_session)}
                {user_session}
                '''
            )
            r.close()
            return True
        except Exception as e:
            _common_modules.logger_error(e)
            r.close()
    except Exception as e:
        _common_modules.logger_error(e)
    return False


'''
Redis Session - Fetch
'''
def fetch_redis_session(package_name):
    user_session = {}
    try:
        r = init_redis()
        try:
            # Check session
            user_session = r.hgetall(package_name)
            _common_modules.logger_info(
                f'''
                Redis fetched session '{package_name}'
                {type(user_session)}
                {user_session}
                '''
            )
            r.close()
        except Exception as e:
            _common_modules.logger_error(e)
            r.close()
    except Exception as e:
        _common_modules.logger_error(e)
    return user_session


'''
Redis Session - Clear
'''
def clear_redis_session(package_name):
    try:
        r = init_redis()
        try:
            # Check session
            r.delete(package_name)
            _common_modules.logger_info(
                f'''
                Redis session deleted '{package_name}'
                '''
            )
            r.close()
            return True
        except Exception as e:
            _common_modules.logger_error(e)
            r.close()
    except Exception as e:
        _common_modules.logger_error(e)
    return False
