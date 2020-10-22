"""
stackl.general_utils
~~~~~~~~~~~~~~
This module provides general utility functions that are used within stackl
"""
import datetime
import socket
from collections import defaultdict


def get_timestamp(timestamp_datetime=None, spaces=True):
    """Get current time"""
    if timestamp_datetime:
        return timestamp_datetime.strftime(_get_timestamp_format(spaces))
    return datetime.datetime.now().strftime(_get_timestamp_format(spaces))


def get_datetime(timestamp=None, spaces=True):
    """Get current date"""
    if not timestamp:
        timestamp = get_timestamp()
    return datetime.datetime.strptime(timestamp, _get_timestamp_format(spaces))


def _get_timestamp_format(spaces=True):
    """Get the format of the timestamp"""
    if spaces:
        return '%Y-%m-%d %Hh%Mm%Ss'
    return '%Y-%m-%d_%Hh%Mm%Ss'


def get_hostname():
    """Returns the hostname of the instance where stackl is running"""
    return socket.gethostname()


def tree():
    """Used for having a dict which elements are also dicts"""
    return defaultdict(tree)
