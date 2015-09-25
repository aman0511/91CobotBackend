#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import unittest
import traceback
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Shell, Server, Manager, prompt_bool
from flask.ext.script.commands import InvalidCommand
from app import app, db, models
from app.tasks import (start_data_task_of_day,
                       start_data_task_of_duration)

manager = Manager(app)

# add `runserver` command to serve this app
manager.add_command("runserver", Server())

# add `db` command to handle database migrations
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# add shell command to open python shell
def _make_context():
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def create_db():
    """Creates database tables from sqlalchemy models"""
    if prompt_bool("Are you sure you want to create new tables"):
        db.create_all()
        print('Database tables successfully created.')


@manager.command
def drop_db():
    """Drops database tables"""
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        print('Database tables successfully dropped.')


@manager.option('-sd', '--startDate', dest='start_date', default=None,
                help="start date of crawl in 'YYYY-MM-DD' format")
@manager.option('-ed', '--endDate', dest='end_date', default=None,
                help="end date of crawl in 'YYYY-MM-DD' format")
def run_task_data(start_date, end_date):
    """Runs a task to get and insert data from cobot api"""
    try:
        if start_date and end_date:
            start_data_task_of_duration(start_date, end_date)
        elif start_date:
            start_data_task_of_day(start_date)
        else:
            print('Check argument options, type command with --help')
            return

        print('===> Task Completed')
    except Exception:
        traceback.print_exc()


@manager.command
def test():
    """Runs the unit tests"""
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    else:
        return 1


if __name__ == '__main__':
    try:
        manager.run()
    except InvalidCommand as err:
        print(err, file=sys.stderr)
        sys.exit(1)
