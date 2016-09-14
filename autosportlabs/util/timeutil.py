__all__ = ('time_to_epoch', 'format_time')
import calendar
from datetime import datetime

def time_to_epoch(timestamp):
    """
    convert a timestamp to a Unix epoch
    :param timestamp in "YYYY-MM-DDTHH:MM:SSS" format
    :type string
    :return returns the epoch time as int
    """
    return int(calendar.timegm(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").timetuple()))

def format_time(dt=datetime.now()):
    """
    format the supplied datetime to the current locale
    :param the time to format. If not speified, defaults to now
    :type datetime
    :return returns the formatted string
    """
    return dt.strftime("%Ex %EX")



