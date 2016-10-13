__all__ = ('time_to_epoch', 'format_time', 'epoch_to_time')
import calendar
from datetime import datetime
from kivy import platform

def time_to_epoch(timestamp):
    """
    convert a timestamp to a Unix epoch. Timestamp formats supported
    "YYYY-MM-DDTHH:MM:SSSZ"
    "YYYY-MM-DDTHH:MM:SSS.SSSZ"
    "YYYY-MM-DDTHH:MM:SSS"
    "YYYY-MM-DDTHH:MM:SSS.SSS"
    :param timestamp  
    :type string
    :return returns the epoch time as int
    """
    if len(timestamp) and timestamp[-1] == 'Z':
        timestamp = timestamp[:-1]
    try:
        t = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        t = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    return int(calendar.timegm(t.timetuple()))

def format_time(dt=datetime.now()):
    """
    format the supplied datetime to the current locale
    :param the time to format. If not speified, defaults to now
    :type datetime
    :return returns the formatted string
    """
    format = '%x %X' if platform == 'win' else '%Ex %EX'
    return dt.strftime(format)

def epoch_to_time(epoch):
    """
    convert an epoch time to formatting time string
    :param epoch the epoch time
    :type epoch int
    :return returns the formatted string
    """    
    dt = datetime.utcfromtimestamp(epoch)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")



