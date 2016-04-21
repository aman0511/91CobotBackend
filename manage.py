#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import traceback
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import (Shell, Server, Manager, Command,
                              Option, prompt_bool)
from flask.ext.script.commands import InvalidCommand
from app import app
from app.models import *
from app.tasks import (start_data_task_of_day,
                       start_data_task_of_duration,
                       start_report_task_of_month,
                       start_report_task_of_duration)
import urllib


class GunicornServer(Command):
    """Run the app within Gunicorn"""

    def get_options(self):
        from gunicorn.config import make_settings

        settings = make_settings()
        options = (
            Option(*klass.cli, action=klass.action)
            for setting, klass in settings.items() if klass.cli
        )
        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication

        app = WSGIApplication()
        app.app_uri = 'manage:app'
        return app.run()


manager = Manager(app)

# add `runserver` command to serve this app
manager.add_command("runserver", Server())

# add `gunicorn` command to run project within gunicorn
manager.add_command("gunicorn", GunicornServer())

# add `db` command to handle database migrations
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# add shell command to open python shell
manager.add_command("shell", Shell())


@manager.command
def list_routes():
    """List all routes in current flask application"""
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint,
                                                        methods, rule))
        output.append(line)

    for line in sorted(output):
        print line


@manager.command
def create_db():
    """Creates database tables from sqlalchemy models"""
    if prompt_bool("Are you sure you want to create new tables"):
        db.create_all()
        print 'Database tables successfully created.'


@manager.command
def drop_db():
    """Drops database tables"""
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Database tables successfully dropped.'


@manager.command
def fill_db():
    """Drops database tables"""
    drop_db()
    db.create_all()

    # create a Locations
    bangalore = Location.create(name="Bangalore")
    gurgaon = Location.create(name="Gurgaon")
    hyderabad = Location.create(name="Hyderabad")
    navi_mumbai = Location.create(name="Navi Mumbai")
    noida = Location.create(name="Noida")
    delhi = Location.create(name="Delhi")

    # create hubs
    Hub.create(name="91sblrst1", location=bangalore)
    Hub.create(name="91sgurgaon", location=gurgaon)
    Hub.create(name="91shyderabad", location=hyderabad)
    Hub.create(name="91smumbai", location=navi_mumbai)
    Hub.create(name="91snoida", location=noida)
    Hub.create(name="91springboard", location=delhi)

    print 'Data filled to tables successfully.'


@manager.option('-sd', '--startDate', dest='start_date', default=None,
                help="start date of crawl in 'YYYY-MM-DD' format")
@manager.option('-ed', '--endDate', dest='end_date', default=None,
                help="end date of crawl in 'YYYY-MM-DD' format")
@manager.option('-h', '--hub', dest='hub_name', default=None,
                help="name of hub")
def run_task_data(start_date, end_date, hub_name):
    """Runs a task to get and insert data from cobot api"""
    try:
        if start_date and end_date:
            start_data_task_of_duration(start_date, end_date, hub_name)
        elif start_date:
            start_data_task_of_day(start_date, hub_name)
        else:
            print 'Check argument options, type command with --help'
            return

        print '===> Task Completed'
    except Exception:
        traceback.print_exc()


@manager.option('-sd', '--startDate', dest='start_date', default=None,
                help="start date of crawl in 'YYYY-MM' format")
@manager.option('-ed', '--endDate', dest='end_date', default=None,
                help="end date of crawl in 'YYYY-MM' format")
@manager.option('-h', '--hub', dest='hub_name', default=None,
                help="name of hub")
def run_task_report(start_date, end_date, hub_name):
    """Runs a task to calculate member report metrics from database data"""
    try:
        if start_date and end_date:
            start_report_task_of_duration(start_date, end_date, hub_name)
        elif start_date:
            start_report_task_of_month(start_date, hub_name)
        else:
            print 'Check argument options, type command with --help'
            return

        print '===> Task Completed'
    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    try:
        manager.run()
    except InvalidCommand as err:
        sys.exit(1)
