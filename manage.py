#!/usr/bin/env python
import unittest
from flask.ext.script import Shell, Server, Manager
from app import app, db, models
from app.tasks import get_data_of_a_day
import traceback

manager = Manager(app)

# add runserver command to serve this app
manager.add_command("runserver", Server())


# add shell command to open python shell
def _make_context():
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=_make_context))


@manager.command
def create_db():
    """Creates database tables from sqlalchemy models"""
    db.create_all()
    print 'Database tables successfully created.'


@manager.command
def drop_db():
    """Drops database tables"""
    db.drop_all()
    print 'Database tables successfully droped.'


@manager.option('-d', '--date', dest='date', default=None)
def run_task(date):
    """Runs a task to get and insert data from cobot api"""
    try:
        if date:
            get_data_of_a_day(date)
            print '===> Task Completed\n'
        else:
            print 'date argument is not provided'
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
    manager.run()
