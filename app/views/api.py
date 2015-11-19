# -*- coding: utf-8 -*-
from __future__ import division
from flask import Blueprint, request
from flask.ext.api import status
from app.models import PLAN_TYPES, Hub
from collections import OrderedDict
from app import app, cache
from app.utils import is_date_in_valid_format
from app.helpers import (get_cnt_of_active_members_in_past,
                         get_cnt_of_new_members_in_past,
                         get_cnt_of_leave_members_in_past,
                         get_all_hub_plans_of_plan_type,
                         get_all_member_reports_of_hub_plans)
import urllib

# create blueprint instance
api = Blueprint('API', __name__, url_prefix='/api')


def make_cache_key():
    """
    A function which returns a unique key to cache result on basis of url
    arguments
    """
    args = request.args
    cache_key = request.path + '?' + urllib.urlencode([
        (k, v) for k in sorted(args) for v in sorted(args.getlist(k))
    ])
    app.logger.debug("Request Url: %s" % (request.url))
    app.logger.debug("Key:: %s" % (cache_key))
    return cache_key


@api.route("/cards", methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def get_cards():
    # extract hub_name` argument from request
    hub_name = request.args.get('hub_name', None)

    # By default, hub=None signify all hubs
    hub = None

    # if hub_name is passed in request arguments, then get hub's instance
    if hub_name:
        hub = Hub.first(name=hub_name)
        if not hub:
            return ({'error': 'No such hub found'},
                    status.HTTP_400_BAD_REQUEST)

    # intializise list to have results to return as response
    res = list()

    # get data and create output of card 1
    present_active_members = get_cnt_of_active_members_in_past(hub, days=0)
    new_members_in_past_months = get_cnt_of_new_members_in_past(hub, days=30)

    print present_active_members, new_members_in_past_months
    card_1 = OrderedDict()
    card_1["card_no"] = 1
    card_1['total_active_members'] = present_active_members
    card_1['new_members'] = {
        'percent': round((new_members_in_past_months /
                          present_active_members)*100, 1),
        'duration': 30
    }
    res.append(card_1)

    # get data and create output of card 2
    card_2 = OrderedDict()
    card_2["card_no"] = 2
    res.append(card_2)

    # get data and create output of card 3
    active_members_till_past_week = get_cnt_of_active_members_in_past(hub,
                                                                      days=7)
    new_members_in_past_weeks = get_cnt_of_new_members_in_past(hub, days=7)

    card_3 = OrderedDict()
    card_3["card_no"] = 3
    card_3['new_members'] = {
        'count': new_members_in_past_weeks,
        'duration': 7,
        'base_percent': round((new_members_in_past_weeks /
                               active_members_till_past_week)*100, 2)
    }
    res.append(card_3)

    # get data and create output of card 4
    leave_members_in_past_weeks = get_cnt_of_leave_members_in_past(hub, days=7)

    card_4 = OrderedDict()
    card_4["card_no"] = 4
    card_4['leave_members'] = {
        'count': leave_members_in_past_weeks,
        'duration': 7,
        'base_percent': round((leave_members_in_past_weeks /
                               active_members_till_past_week)*100, 2)
    }
    res.append(card_4)

    # return response
    return (res, status.HTTP_200_OK)


@api.route("/reports", methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def get_reports():
    # extract hub_name` argument from request
    hub_name = request.args.get('hub_name', None)

    #  extract plan_type
    plan_type = request.args.get('plan_type', None)

    #  extract from
    from_d = request.args.get('from', None)

    #  extract to
    to_d = request.args.get('to', None)

    # By default, hub=None signify all hubs
    hub = None

    # if hub_name is passed in request arguments, then get hub's instance
    if hub_name:
        hub = Hub.first(name=hub_name)
        if not hub:
            return ({'error': 'No such hub found'},
                    status.HTTP_400_BAD_REQUEST)

    if plan_type:
        if plan_type not in PLAN_TYPES:
            return ({'error': 'No such plan type found'},
                    status.HTTP_400_BAD_REQUEST)

    if from_d or to_d:
        if not (is_date_in_valid_format(from_d, '%Y-%m') or
                is_date_in_valid_format(to_d, '%Y-%m')):
            return ({'error': 'Date should be in YYYY-MM format'},
                    status.HTTP_400_BAD_REQUEST)

    # intializise list to have results to return as response
    res = list()

    # get all hub plans for all above plans
    hub_plans = get_all_hub_plans_of_plan_type(hub, plan_type)

    # get member report's for all hub_plan's
    m_reports = get_all_member_reports_of_hub_plans(hub_plans, from_d, to_d)

    # serialize all member report's and append to them in result
    for mr in m_reports:
        res.append(mr.serialize())

    return (res, status.HTTP_200_OK)


@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    res = {
        "error": "Service temporarily unavailable, try again later."
    }
    return (res, status.HTTP_500_INTERNAL_SERVER_ERROR)
