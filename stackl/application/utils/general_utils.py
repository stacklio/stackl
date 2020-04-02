"""
stackl.general_utils
~~~~~~~~~~~~~~
This module provides general utility functions that are used within stackl
"""
import datetime
import logging
import os
import random
import socket
import string
import time


logger = logging.getLogger("STACKL_LOGGER")


def get_config_key(key):
    value = os.environ.get('STACKL_' + key.upper(), None)
    logger.info(f"[General Utils] get_config_key. Key: '{key}'. Value: '{value}'")
    if value:
        return value

def generate_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def get_timestamp(timestamp_datetime=None, spaces=True):
    if timestamp_datetime:
        return timestamp_datetime.strftime(_get_timestamp_format(spaces))
    else:
        return datetime.datetime.now().strftime(_get_timestamp_format(spaces))

def get_datetime(timestamp=None, spaces=True):
    if not timestamp:
        timestamp = get_timestamp()
    return datetime.datetime.strptime(timestamp, _get_timestamp_format(spaces))

def get_absolute_time_seconds():
    return time.time()

def _get_timestamp_format(spaces=True):
    if spaces:
        return '%Y-%m-%d %Hh%Mm%Ss'
    return '%Y-%m-%d_%Hh%Mm%Ss'

def get_hostname():
    return socket.gethostname()
