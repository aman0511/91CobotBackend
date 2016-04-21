# -*- coding: utf-8 -*-
"""
Two Tasks for cobot data
 * get data and insert data into database
 * calculate member report metrics
"""
import requests
import traceback
import config
from app.models import (
    Hub,
    Plan,
    Time,
    User,
    HubPlan,
    Membership,
    MembershipPlan,
    MemberReport
)
from app.utils import (
    get_date_obj_from_str,
    increment_date,
    get_first_date_of_month,
    get_last_date_of_month,
    get_current_date_str,
    is_date_format_valid,
    dump_data_to_file,
    get_data_from_file_if_exists
)
from app.helpers import (
    preprocess_membership_data,
    is_membership_plan_changed,
    set_end_date_of_last_membership_plan,
    get_and_set_new_members_report_for_a_hub_plan,
    get_and_set_retain_members_report_for_a_hub_plan,
    get_and_set_leave_members_report_for_a_hub_plan
)
from logger import logger


def process_data_of_hub(hub, data, date_of_crawl=None):
    """
    Process data given by cobot api
    """
    # check if date of crawl is set or not
    # if not then set it with current date
    if date_of_crawl is None:
        date_of_crawl = get_current_date_str()

    for index, membership_data in enumerate(data):
        try:
            # preprocess a membership data in a model suitable
            # form
            m_data = preprocess_membership_data(membership_data)

            # check user exists or not if not create user else get it's
            # instance
            user = User.create_or_get(**m_data["user"])

            # check membership exists or not if not create membership else
            # get it's instance
            membership = Membership.create_or_get(**m_data['membership'])

            # assign a hub to this membership if not else do nothing
            membership.assign_hub(hub)

            # assign a user to this membership if not else do nothing
            membership.assign_user(user)

            # check plan exists or not if not create plan else get it's
            # instance
            plan = Plan.create_or_get(**m_data['plan'])

            # check hub_plan exists or not if not create hub_plan else get
            # it's instance
            context = {
                'hub': hub,
                'plan': plan
            }
            hub_plan = HubPlan.create_or_get(**context)

            # check if plan of a membership changed or not
            if is_membership_plan_changed(membership, hub_plan):
                # if plan changed then set end_date of last active plan of
                # a membership as date_of_crawl, if any
                last_membership_plan = set_end_date_of_last_membership_plan(
                                membership, date_of_crawl)

                # create a new membership plan instance
                context = {
                    'membership': membership,
                    'hub_plan': hub_plan,
                    'start_date': get_date_obj_from_str(date_of_crawl)
                }

                # and, also set `start_date` of membership plan depending upon
                # last_membership_plan existence
                if not last_membership_plan:
                    context['start_date'] = \
                        m_data['membership']['confirmed_at']

                # create a new membership plan
                membership_plan = MembershipPlan.create(**context)
            else:
                # nothing to do
                pass

            # check if membership ended or not and, if yes set canceled_to date
            # of membership and also set end_date of last membership_plan of
            # this membership_plan
            m_canceled_date = get_date_obj_from_str(
                membership_data['canceled_to'])
            membership.set_canceled_date(m_canceled_date)

        except Exception as e:
            logger.error(e, exc_info=True)

    logger.info("Total {0} Memberships processed on {1} of hub {2}".format(
        len(data), date_of_crawl, hub.name))


def get_data_from_api_of_hub(date_str, hub):
    """
    Get data of memberships plans from cobot api of a particular specified day
    """
    # check date should be in valid format(i.e YYYY-MM-DD)
    if not is_date_format_valid(date_str):
        return None

    # check if hub instance is passed or not
    if not isinstance(hub, Hub):
        return None

    token = 'Bearer %s' % config.COBOT_TOKEN

    # create a API end-point url to get data
    membership_url = config.MEMBERSHIPS_URL_STR % hub.name

    # set Authorization header field
    headers = {
        'Authorization': token
    }

    # set arbitrary arguments to be passed with request
    params = {
        'as_of': date_str
    }

    # create a file name with hub_name as directory
    # <hub_name>/membership-<date_str>.json
    file_name = "{0}/memberships-{1}.json".format(hub.name, date_str)

    # get data from dumped file if exists
    data = get_data_from_file_if_exists(file_name)

    if data:
        return data

    logger.info("Requesting data from cobot of url {0} and date {0}".format(
        membership_url, date_str))

    # call end-point, send request and collect response
    response = requests.get(membership_url, headers=headers, params=params)

    # if call was made successfully, return data in JSON format
    if response.status_code == 200:
        logger.info('Data returned from api successfully of hub %s' % hub.name)
        data = response.json()

        # also dump data to file
        dump_data_to_file(data, file_name=file_name)
        return data
    else:
        logger.info('Data could not returned from api successfully of hub '
                    '{0} with status code {1}'.format(hub.name,
                                                      response.status_code))

    return None


def get_and_process_data_of_day(date_str, hub_name):
    """
    Get data of a particular given day and also process that data
    """
    # check date should be in valid format(i.e YYYY-MM-DD)
    if not is_date_format_valid(date_str):
        return None

    # check if hub_name is passed or not, if not then get all hubs to
    # process, otherwise just process data only for that passed hub
    hubs = Hub.find(name=hub_name) if hub_name else Hub.get_all()

    for hub in hubs:
        # get data of a hub for a day
        data = get_data_from_api_of_hub(date_str, hub=hub)

        if data:
            # process a data of a hub
            process_data_of_hub(hub, data, date_of_crawl=date_str)


def start_data_task_of_day(date_str, hub_name):
    """
    Start task to get data of a particular specified day from cobot api
    and insert that data into database
    """
    crawl_date = get_date_obj_from_str(date_str)

    # if crawl date is set then get data of crawl date and process it
    return get_and_process_data_of_day(crawl_date.isoformat(), hub_name)


def start_data_task_of_duration(s_date, e_date, hub_name):
    """
    Start task to get data of a particular specified duration from cobot api
    and insert that data into database
    """
    crawl_date = get_date_obj_from_str(s_date)
    end_date = get_date_obj_from_str(e_date)

    while crawl_date <= end_date:
        # get data of crawl date and process it
        get_and_process_data_of_day(crawl_date.isoformat(), hub_name)

        # increment crawl date by 1 day
        crawl_date = increment_date(crawl_date, days=1)


def get_and_set_member_report_metrics_of_hub_plan(hub_plan, date_str):
    """
    Calculate member report metrics for a given month from present data
    in database
    """
    if not(isinstance(hub_plan, HubPlan)):
        return None

    # get start date of month
    start_date_of_month = get_first_date_of_month(date_str)

    # get end date of month
    end_date_of_month = get_last_date_of_month(date_str)

    # check time exists or not if not create time else get it's instance
    time = Time.create_or_get(date=start_date_of_month)

    # check member_report exists or not if not create member_report else
    # get it's instance
    member_report = MemberReport.create_or_get(time=time, hub_plan=hub_plan)

    # reset all counters of member_report to be `0`, so that we can start
    # with fresh member_report instance
    member_report.reset_all_counter()

    # get and set count of all new membership plans of a particular hub and
    # plan within a given time frame(i.e here is for a month)
    get_and_set_new_members_report_for_a_hub_plan(member_report,
                                                  hub_plan,
                                                  start_date_of_month,
                                                  end_date_of_month)

    # get and set count of all retain membership plans of a particular hub
    # and plan within a given time frame(i.e here is for a month)
    get_and_set_retain_members_report_for_a_hub_plan(member_report,
                                                     hub_plan,
                                                     start_date_of_month,
                                                     end_date_of_month)

    # get and set count of all leave membership plans of a particular hub
    # and plan within a given time frame(i.e here is for a month)
    get_and_set_leave_members_report_for_a_hub_plan(member_report,
                                                    hub_plan,
                                                    start_date_of_month,
                                                    end_date_of_month)


def calculate_member_report_metrics_of_a_month(date_str, hub_name):
    """
    Calculate member report metrics for a given month from present data
    in database for all hub_plan's
    """
    if not is_date_format_valid(date_str, '%Y-%m'):
        return None

    # store all hub_plan's to process
    hub_plans = []

    # get all hub_plan's to process
    if hub_name:
        h = Hub.first(name=hub_name)
        hub_plans = HubPlan.find(hub=h)
    else:
        hub_plans = HubPlan.get_all()

    # calculate member report metrics for each plan of all hub
    for hub_plan in hub_plans:
        get_and_set_member_report_metrics_of_hub_plan(hub_plan, date_str)

    print "Total %s plans of all hub processed." % len(hub_plans)


def start_report_task_of_month(date_str, hub_name):
    """
    Start task to calculate member report metrics of a particular given
    month from data in database
    """
    print 'Report processed on %s \n' % date_str
    return calculate_member_report_metrics_of_a_month(date_str, hub_name)


def start_report_task_of_duration(s_date, e_date, hub_name):
    """
    Start task to calculate member report metrics of a particular given
    duration from data in database
    """
    crawl_date = get_date_obj_from_str(get_first_date_of_month(s_date))
    end_date = get_date_obj_from_str(get_last_date_of_month(e_date))

    while crawl_date <= end_date:
        # convert crawl date of format `YYYY-MM-DD` to `YYYY-MM`
        crawl_date_str = crawl_date.isoformat().rsplit('-', 1)[0]

        # get data of crawl date and process it
        calculate_member_report_metrics_of_a_month(crawl_date_str, hub_name)

        print 'Report processed on %s\n' % crawl_date_str

        # increment crawl date by 1 day
        crawl_date = increment_date(crawl_date, weeks=4)

