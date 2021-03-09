from requests import get, exceptions
from util.decorators import retry

import config

def is_authorized():
    instance_id = get_instance_id()

    if instance_id == config.INSTANCE_ID:
        return True
    return False

@retry(3, 3, 'get instance id', (exceptions.ConnectionError, exceptions.Timeout))
def get_instance_id():
    return get('http://169.254.169.254/latest/meta-data/instance-id').text