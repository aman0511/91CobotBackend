# Basic utilities functions
import datetime


def get_current_date():
    """Return curret date instance of datetime.date"""
    d = datetime.datetime.now()
    return datetime.date(d.year, d.month, d.day)


def get_date(date_str):
    """Return datetime.date object of date_str"""
    if date_str:
        date = date_str.split()[0]
        return datetime.datetime.strptime(date, '%Y/%m/%d').date()
    else:
        None
