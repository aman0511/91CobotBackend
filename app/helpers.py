# -*- coding: utf-8 -*-
from flask import url_for
from app import app
from app.models import (Membership, HubPlan, Hub)
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
