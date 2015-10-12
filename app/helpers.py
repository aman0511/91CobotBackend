# -*- coding: utf-8 -*-
from flask import url_for
from app import app
from app.models import (Membership, HubPlan, Hub, Plan,
                        MembershipPlan, MemberReport)
from app.utils import get_date_obj, decrement_date, get_current_date
from sqlalchemy import and_, or_

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename=filename)
)


def preprocess_membership_data(membership_data):
    """
    Preprocess membership data and return data in modular form
    """
    res = dict()

    # collect user data
    res['user'] = {
        'name': membership_data['name'],
        'email': membership_data['email'] if membership_data['email']
        else None
    }

    # collect membership data
    res['membership'] = {
        'cobot_id': membership_data['id'],
        'confirmed_at': get_date_obj(membership_data['confirmed_at']),
        'canceled_to': get_date_obj(membership_data['canceled_to'])
    }

    # collect plan data
    res['plan'] = {
        'name': membership_data['plan']['name'].strip(),
        'price': membership_data['plan']['total_price_per_cycle']
    }

    return res


def is_membership_plan_changed(membership, hub_plan):
    """
    Check if a plan of a membership changed or not
    """
    if isinstance(membership, Membership) and isinstance(hub_plan, HubPlan):
        last_membership_plan = membership.get_last_membership_plan()

        if last_membership_plan and last_membership_plan.hub_plan.plan.name \
                == hub_plan.plan.name:
            return False
        else:
            return True
    else:
        None


def set_end_date_of_last_membership_plan(membership, end_date=None):
    """
    Set a end_date of last membership plan
    """
    if isinstance(membership, Membership):
        last_membership_plan = membership.get_last_membership_plan()
        if last_membership_plan:
            last_membership_plan.set_end_date(get_date_obj(end_date))
        return last_membership_plan
    return None


def get_cnt_of_active_members_in_past(hub=None, days=0):
    """
    Returns a number of active members in a hub on a given date
    date should be in `YYYY-MM-DD` format.
    """
    base_date = decrement_date(get_current_date(), days=-days).isoformat()

    query = None
    print base_date

    # if no hub passed, then return all hubs active members count
    if not hub:
        query = or_(Membership.canceled_to == None,
                    Membership.canceled_to >= base_date)

    # if hub's instance then return count of active members of a hub
    if isinstance(hub, Hub):
        query = or_(Membership.hub == hub, Membership.canceled_to == None,
                    Membership.canceled_to >= base_date)

    print query
    # if query exist, return results
    if query is not None:
        return int(Membership.count(query))

    # otherwise return None
    return None


def get_cnt_of_new_members_in_past(hub=None, days=30):
    """
    Returns a count of a new members in a given past days
    """
    base_date = decrement_date(get_current_date(), days=-days).isoformat()

    query = None

    # if no hub passed, then return all hubs new members count
    if not hub:
        query = and_(Membership.confirmed_at >= base_date)

    # if hub's instance then return count of new members of a hub
    if isinstance(hub, Hub):
        query = and_(Membership.hub == hub,
                     Membership.confirmed_at >= base_date)

    # if query exist, return results
    if query is not None:
        return int(Membership.count(query))

    # otherwise return None
    return None


def get_cnt_of_leave_members_in_past(hub=None, days=30):
    """
    Returns a count of a leave members in a given past days
    """
    base_date = decrement_date(get_current_date(), days=-days).isoformat()

    query = None

    # if no hub passed, then return all hubs new members count
    if not hub:
        query = and_(Membership.canceled_to >= base_date)

    # if hub's instance then return count of new members of a hub
    if isinstance(hub, Hub):
        query = and_(Membership.hub == hub,
                     Membership.canceled_to >= base_date)

    # if query exist, return results
    if query is not None:
        return int(Membership.count(query))

    # otherwise return None
    return None


def get_all_hub_plans_of_plan_type(hub=None, plan_type=None):
    """
    Return all hub plans of a particular hub and whose plan is of given
    plan_type
    """
    query = and_()

    if plan_type:
        query = and_(Plan.type == plan_type)

    # get all plans of a given plan_type
    plans = Plan.find(query)

    res = list()

    for plan in plans:
        if isinstance(hub, Hub):
            query = and_(HubPlan.hub == hub, HubPlan.plan == plan)
        else:
            query = and_(HubPlan.plan == plan)

        hub_plans = HubPlan.find(query)
        res.extend(hub_plans)
    return res


def get_all_member_reports_of_hub_plans(hub_plans):
    """
    """
    hub_plan_ids = [hp.id for hp in hub_plans if isinstance(hp, HubPlan)]

    return MemberReport.find(MemberReport.hub_plan_id.in_(hub_plan_ids))


def get_new_membership_plans_in_a_time_frame(hub_plan, start_date, end_date):
    """
    Get all membership plans which are recently created within a given time
    frame
    """
    return MembershipPlan.find(and_(MembershipPlan.hub_plan == hub_plan,
                                    MembershipPlan.start_date >= start_date,
                                    MembershipPlan.start_date <= end_date))


def get_retain_membership_plans_in_a_time_frame(hub_plan, start_date,
                                                end_date):
    """
    Get all membership plans which user still have within a given time frame
    """
    return MembershipPlan.find(and_(MembershipPlan.hub_plan == hub_plan,
                                    MembershipPlan.start_date < start_date,
                                    or_(MembershipPlan.end_date == None,
                                        MembershipPlan.end_date > end_date)))


def get_leave_membership_plans_in_a_time_frame(hub_plan, start_date,
                                               end_date):
    """
    Get all membership plans which user leave within a given time frame
    """
    return MembershipPlan.find(and_(MembershipPlan.hub_plan == hub_plan,
                                    MembershipPlan.end_date >= start_date,
                                    MembershipPlan.end_date <= end_date))


def get_and_set_new_members_report_for_a_hub_plan(member_report, hub_plan,
                                                  start_date, end_date):
    """
    Set the metrices of new users for a plan in a particular hub within a
    given time frame
    """
    if not (isinstance(member_report, MemberReport) and
            isinstance(hub_plan, HubPlan)):
        return None

    if start_date and end_date:
        new_members_hp = get_new_membership_plans_in_a_time_frame(hub_plan,
                                                                  start_date,
                                                                  end_date)
        new_members_hp_cnt = len(new_members_hp)
        # print 'New Members %d between  %s and %s' % (new_members_hp_cnt,
        #                                              start_date, end_date)
        member_report.increment_nm_cnt_by(new_members_hp_cnt)
        member_report.increment_nm_rev_by(new_members_hp_cnt * hub_plan.
                                          plan.price)
    return None


def get_and_set_retain_members_report_for_a_hub_plan(member_report, hub_plan,
                                                     start_date, end_date):
    """
    Set the metrices of retain users for a plan in a particular hub within a
    given time frame
    """
    if not (isinstance(member_report, MemberReport) and
            isinstance(hub_plan, HubPlan)):
        return None

    if start_date and end_date:
        retain_members_hp = get_retain_membership_plans_in_a_time_frame(
            hub_plan,
            start_date,
            end_date)
        retain_members_hp_cnt = len(retain_members_hp)
        # print 'Retain Members %d between %s and %s' % (retain_members_hp_cnt,
        #                                                start_date, end_date)
        member_report.increment_rm_cnt_by(retain_members_hp_cnt)
        member_report.increment_rm_rev_by(retain_members_hp_cnt * hub_plan.
                                          plan.price)
    return None


def get_and_set_leave_members_report_for_a_hub_plan(member_report, hub_plan,
                                                    start_date, end_date):
    """
    Set the metrices of leave users for a plan in a particular hub within a
    given time frame
    """
    if not (isinstance(member_report, MemberReport) and
            isinstance(hub_plan, HubPlan)):
        return None

    if start_date and end_date:
        leave_members_hp = get_leave_membership_plans_in_a_time_frame(
            hub_plan,
            start_date,
            end_date)
        leave_members_hp_cnt = len(leave_members_hp)
        # print 'Leave Members %d between %s and %s' % (leave_members_hp_cnt,
        #                                               start_date, end_date)
        member_report.increment_lm_cnt_by(leave_members_hp_cnt)
        member_report.increment_lm_rev_by(leave_members_hp_cnt * hub_plan.
                                          plan.price)
    return None
