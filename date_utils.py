from datetime import datetime, timedelta

date_time_format = '%Y-%m-%dT%H:%M:%SZ'


def get_date_from_string(date):
    if not date:
        return None
    return datetime.strptime(date, date_time_format)


def get_string_from_date(date):
    return datetime.strftime(date, date_time_format)


def get_utc_now():
    return datetime.utcnow()


def get_days_diff(dateA, dateB):
    return (dateA - dateB).days


def get_hours_diff(dateA, dateB):
    return int((dateA - dateB).total_seconds() // 3600)


def subtract_hours_from_date(date, hours):
    return date - timedelta(hours=hours)
