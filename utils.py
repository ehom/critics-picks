import time
from datetime import datetime
from calendar import timegm


def iso_to_epoch_time(iso_date_str):
    # Parse the ISO date string and convert it to a datetime object
    parsed_datetime = datetime.fromisoformat(iso_date_str)

    # Get the UTC timestamp from the datetime object
    timestamp = timegm(parsed_datetime.utctimetuple())

    return timestamp


def iso_to_how_long_ago(iso_date_str):
    t0_past = iso_to_epoch_time(iso_date_str)
    t1_now = int(time.time())

    time_difference = t1_now - t0_past

    # Get the time components (days, seconds, etc.) from the time difference
    days = round(time_difference / (60 * 60 * 24))
    seconds = round(time_difference)

    if days > 7:
        weeks = days // 7
        return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
    elif days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return "Just now"
