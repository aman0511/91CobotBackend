# -*- coding: utf-8 -*-
"""
Two Tasks for cobot data
 * get data and insert data into database
 * calculate member report metrics
"""
from __future__ import print_function
import requests
import traceback
import config
from app.models import (User, Hub, Plan, HubPlan, Membership, MembershipPlan)
from app.utils import (get_first_date_of_month,
                       get_last_date_of_month,
                       get_current_date_in_str,
                       get_date_obj,
                       get_date_str,
                       increment_date,
                       is_date_in_valid_format)
from app.helpers import (preprocess_membership_data,
                         is_membership_plan_changed,
                         set_end_date_of_last_membership_plan)


def process_data_of_hub(hub, data, date_of_crawl=None):
    """
    Process data given by cobot api
    """

    # check if date of crawl is set or not
    # if not then set it with current date
    if not date_of_crawl:
        date_of_crawl = get_current_date_in_str()

    for index, membership_data in enumerate(data):
        try:
            # print('Processing membership no. %d' % (index+1))

            # preprocess a membership data in a model suitable
            # form
            m_data = preprocess_membership_data(membership_data)
            # print(m_data)

            # check user exists or not if not create user else get it's
            # instance
            user = User.create_or_get(**m_data['user'])
            # print(user)

            # check membership exists or not if not create membership else
            # get it's instance
            membership = Membership.create_or_get(**m_data['membership'])

            # assign a user to this membership if not else do nothing
            membership.assign_user(user)

            # check if membership ended or not and update it, if yes
            membership.set_canceled_date(m_data['membership']['canceled_to'])

            # print(membership)

            # check plan exists or not if not create plan else get it's
            # instance
            plan = Plan.create_or_get(**m_data['plan'])
            # print(plan)

            # check hub_plan exists or not if not create hub_plan else get
            # it's instance
            context = {
                'hub': hub,
                'plan': plan
            }
            hub_plan = HubPlan.create_or_get(**context)
            # print(hub_plan)

            # check if plan of a membership changed or not
            if is_membership_plan_changed(membership, hub_plan):
                # if plan changed then set end_date of last active plan of
                # a membership as date_of_crawl
                last_membership_plan = set_end_date_of_last_membership_plan(
                                membership, date_of_crawl)
                # print(last_membership_plan)

                # create a new membership plan instance
                context = {
                    'membership': membership,
                    'hub_plan': hub_plan,
                    'start_date': get_date_obj(date_of_crawl)
                }
                membership_plan = MembershipPlan.create(**context)
                # print(membership_plan)
            else:
                # nothing to do
                pass

            # print('\n')

        except Exception:
            traceback.print_exc()
            return

    print('Total %d Memberships processed on %s\n' % (len(data),
                                                      date_of_crawl))


def get_data_from_api_of_hub(date, hub):
    """
    Get data of memberships plans from cobot api of a particular specified day
    """
    # check date should be in valid format(i.e YYYY-MM-DD)
    if not is_date_in_valid_format(date):
        return None

    # check if hub instance is passed or not
    if not isinstance(hub, Hub):
        return None

    token = 'Bearer %s' % (config.COBOT_TOKEN)

    # create a API end-point url to get data
    MEMBERSHIPS_URL = config.MEMBERSHIPS_URL_STR % (hub.name)

    # set Authorization header field
    headers = {
        'Authorization': token
    }

    # set arbitrary agruments to be passed with request
    params = {
        'as_of': date
    }

    # call end-point, send request and collect response
    response = requests.get(MEMBERSHIPS_URL, headers=headers, params=params)

    # if call was made successfully, return data in JSON format
    if response.status_code == 200:
        print('Data returned from api successfully')
        data = response.json()
        return data
    else:
        print('Status Code = %d' % (response.status_code))

    return None


def get_and_process_data_of_day(date):
    """
    Get data of a particular given day and also process that data
    """
    # check date should be in valid format(i.e YYYY-MM-DD)
    if not is_date_in_valid_format(date):
        return None

    # get all hubs
    hubs = Hub.get_all()

    for hub in hubs:
        # get data of a hub for a day
        data = get_data_from_api_of_hub(date, hub=hub)

        if data:
            # process a data of a hub
            process_data_of_hub(hub, data, date_of_crawl=date)


def start_data_task_of_day(date):
    """
    Start task to get data of a particular specified day from cobot api
    and insert that data into database
    """
    crawl_date = get_date_obj(date)

    # if crawl date is set then get data of crawl date and process it
    return get_and_process_data_of_day(crawl_date.isoformat())


def start_data_task_of_duration(s_date, e_date):
    """
    Start task to get data of a particular specified duration from cobot api
    and insert that data into database
    """
    crawl_date = get_date_obj(s_date)
    end_date = get_date_obj(e_date)

    while (crawl_date <= end_date):
        # get data of crawl date and process it
        get_and_process_data_of_day(crawl_date.isoformat())

        # increment crawl date by 1 day
        crawl_date = increment_date(crawl_date, days=1)
