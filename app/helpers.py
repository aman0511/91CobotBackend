# -*- coding: utf-8 -*-
from flask import url_for
from app import app
from app.models import (Membership, HubPlan)
from app.utils import get_date_obj

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
