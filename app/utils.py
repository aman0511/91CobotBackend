# -*- coding: utf-8 -*-
"""
Basic utilities functions
"""
import os
import json
import datetime
import config
from calendar import monthrange
from logger import logger


def get_current_date_obj():
    """
    Return current date instance of datetime.date
    """
    return datetime.date.today()


def get_current_date_str():
    """
    Return current date in string (i.e YYYY-MM-DD format)
    """
    return get_current_date_obj().strftime('%Y-%m-%d')


def get_datetime_obj_from_str(datetime_str, _format='%Y-%m-%d'):
    try:
        return datetime.datetime.strptime(datetime_str, _format)
    except ValueError:
        raise ValueError("Incorrect date format of %s" % datetime_str)


def get_date_obj_from_str(date_str):
    """
    Return datetime.date object of date_text
    date_text should be in 'YYYY-MM-DD' or 'YYYY/MM/DD' format.
    """
    if not isinstance(date_str, basestring):
        raise ValueError("%s is not of type string" % date_str)

    #
    date_str = date_str.split()[0].strip()

    if '-' in date_str:
        return get_datetime_obj_from_str(date_str, _format='%Y-%m-%d').date()
    elif '/' in date_str:
        return get_datetime_obj_from_str(date_str, _format='%Y/%m/%d').date()

    raise ValueError("%s is not valid date string" % date_str)


def get_date_str_from_obj(date_obj, _format='%Y-%m'):
    """
    Return date string
    """
    if not isinstance(date_obj, datetime.date):
        raise ValueError("date_obj is not of type datetime.date")

    return date_obj.strftime(_format)


def is_date_format_valid(date_str, _format='%Y-%m-%d'):
    """
    Validate a date_text is in correct specified format or not
    """
    try:
        get_datetime_obj_from_str(date_str, _format=_format)
        return True
    except ValueError:
        return False


def get_first_date_of_month(date_str):
    """
    Return a first day date of a month
    date_str should be in 'YYYY-MM' format.
    """
    if date_str is None:
        return date_str
    return date_str+'-01'


def get_last_date_of_month(date_str):
    """
    Return a last day date of a month
    date_str should be in 'YYYY-MM' format.
    """
    if date_str is None:
        return date_str

    date_str_list = date_str.split('-')
    year, month = map(lambda s: int(s.lstrip('0')), date_str_list)
    return '%s-%d' % (date_str, monthrange(year, month)[1])


def increment_date(date, **kwargs):
    """
    Increment date by no. of specified days
    """
    if isinstance(date, datetime.date):
        return date + datetime.timedelta(**kwargs)
    return None


def decrement_date(date, **kwargs):
    """
    Decrement date by no. of specified days
    """
    return increment_date(date, **kwargs)


def dump_data_to_file(data, file_name=None):
    basedir = config.DUMP_FOLDER_PATH or os.getcwd()
    f_path, f_name = file_name.rsplit("/", 1)
    abs_file_path = os.path.join(basedir, "dump", f_path)

    if not os.path.isdir(abs_file_path):
        os.makedirs(abs_file_path)

    abs_file_path = os.path.join(abs_file_path, f_name)

    with open(abs_file_path, 'w+') as f:
        json.dump(data, f)
    logger.info("Data dumped to {0}".format(abs_file_path))


def get_data_from_file_if_exists(file_name):
    basedir = config.DUMP_FOLDER_PATH or os.getcwd()
    f_path, f_name = file_name.rsplit("/", 1)
    abs_file_path = os.path.join(basedir, "dump", f_path)
    abs_file_path = os.path.join(abs_file_path, f_name)

    if not os.path.exists(abs_file_path):
        logger.info("No dumped file found at {0}".format(abs_file_path))
        return None

    with open(abs_file_path, "r") as f:
        data = json.load(f)
    logger.info("Dumped file found at {0}".format(abs_file_path))
    return data
