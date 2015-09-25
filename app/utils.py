# -*- coding: utf-8 -*-
"""
Basic utilities functions
"""
import datetime
from calendar import monthrange


def is_date_in_valid_format(date_text, format='%Y-%m-%d'):
    """
    Validate a date_text is in correct specified format or not
    """
    try:
        return datetime.datetime.strptime(date_text, format).date()
    except ValueError:
        raise ValueError("Incorrect date format, use --help to get format")


def get_current_date():
    """
    Return curret date instance of datetime.date
    """
    d = datetime.datetime.now()
    return datetime.date(d.year, d.month, d.day)


def get_current_date_in_str():
    """
    Return curret date in string (i.e YYYY-MM-DD format)
    """
    return get_current_date().strftime('%Y-%m-%d')


def get_date_obj(text, format='%Y-%m-%d'):
    """
    Return datetime.date object of date_text
    date_text should be in 'YYYY-MM-DD' or 'YYYY/MM/DD' format.
    """
    if not isinstance(text, (str, unicode)):
        return None
    date_text = text.split()[0].strip()
    if '-' in date_text:
        return is_date_in_valid_format(date_text, format='%Y-%m-%d')
    elif '/' in date_text:
        return is_date_in_valid_format(date_text, format='%Y/%m/%d')
    else:
        return None


def get_date_str(date, format='%Y-%m'):
    """
    Return date string
    """
    if not isinstance(date, datetime.date):
        return None

    return date.strftime(format)


def get_first_date_of_month(date_str):
    """
    Return a first day date of a month
    date_str should be in 'YYYY-MM' format.
    """
    if date_str:
        return date_str+'-01'
    else:
        return None


def get_last_date_of_month(date_str):
    """
    Return a last day date of a month
    date_str should be in 'YYYY-MM' format.
    """
    if date_str:
        date_strs = date_str.split('-')
        year, month = map(lambda s: int(s.lstrip('0')), date_strs)
        return '%s-%d' % (date_str, monthrange(year, month)[1])
    else:
        return None


def increment_date(date, **kwargs):
    """
    Increment date by no. of specified days
    """
    if isinstance(date, datetime.date):
        return date + datetime.timedelta(**kwargs)
    return None
