from functools import wraps
from time import sleep

def retry(retry_count = 2, delay = 5, action_description = 'not specified', allowed_exceptions=()):
    def decorator(func):
        @wraps(func) # to preserve metadata of the function to be decorated
        def wrapper(*args, **kwargs):
            for _ in range(retry_count): 
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    print('Error executing {}: {}'.format(func.__name__, e))
                    print('Waiting for {} sec before executing {} again'.format(delay, func.__name__))
                    sleep(delay)
                    print('Retrying to execute ' + func.__name__ + ' (action: ' + action_description + ')')
        return wrapper
    return decorator