# Tasks to get data and insert data into database
import os
import json
import requests
import traceback
from app.utils import get_current_date
from app.helpers import *


def process_data(_hub, data):
    """Process data given by cobot api"""

    hub = create_or_get_hub(_hub)

    # add it to db session
    add_to_db_session([hub])

    # commit all changes to DB
    commit_to_db()

    index = 0
    for membership_data in data:
        try:
            print 'Processing membership no. %s' % (index+1)
            index = index+1
            # create a list of instances to be add and commot to DB
            bucket = list()

            # get or create a user
            user = create_or_get_user(membership_data)
            bucket.append(user)

            # get or create a membership
            membership = create_or_get_membership(membership_data, user)

            # check if membership ended or not and update it
            if membership and membership_data['canceled_to']:
                membership.canceled_to = membership_data['canceled_to']

            bucket.append(membership)

            # get or create plan
            plan = create_or_get_plan(membership_data['plan'])
            bucket.append(plan)

            # get or create hub_plan
            hub_plan = None
            if is_new_plan(plan):
                hub_plan = create_hub_plan(hub, plan)
            else:
                hub_plan = get_hub_plan_from_instances(hub, plan)
            bucket.append(hub_plan)

            # check if plan changed or not
            if is_membership_plan_changed(membership, hub_plan):
                # set end_date of last plan
                last_membership_plan = set_end_date_of_last_membership_plan(
                                membership, get_current_date())

                # check if last membership plan exist or not
                if last_membership_plan:
                    bucket.append(last_membership_plan)

                # create a new membership plan
                membership_plan = create_membership_plan(membership, hub_plan)
                bucket.append(membership_plan)

            else:
                # nothing to do
                pass

            print '['
            for item in bucket:
                print '    ', item, '\n'
            print ']\n'
            # add bucket to DB session
            add_to_db_session(bucket)

            # commit all changes to DB
            commit_to_db()

        except Exception:
            traceback.print_exc()


def get_data_from_file(filename):
    """Get data from file"""
    try:
        with open(filename) as f:
            data = json.load(f)
        return data
    except Exception:
        traceback.print_exc()


def get_data_from_api(date, hub=None, token=None):
    """Get data from api"""
    if not hub:
        hub = {
            'name': '91sgurgaon',
            'location': 'Gurgaon'
        }

    if not token:
        token = 'Bearer %s' % (os.getenv('COBOT_TOKEN', None))

    MEMBERSHIPS_URL = 'http://%s.cobot.me/api/memberships' % (hub['name'])

    headers = {
        'Authorization': token
    }
    params = {
        'as_of': date
    }
    response = requests.get(MEMBERSHIPS_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        None


def get_data_of_a_day(date, hub=None, token=None):
    """Get Data of a particular given day"""
    hub = {
        'name': '91springboard',
        'location': 'Okhla'
    }
    # data = get_data_from_file('app/dump-2015-09-01.json')
    data = get_data_from_api(date, hub=None)

    if hub:
        process_data(hub, data)
    else:
        print 'Error in creating space entry.'


def start_data_task():
    """Start get data task"""
    pass
