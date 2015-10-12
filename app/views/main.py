# -*- coding: utf-8 -*-
from __future__ import division
from flask import Blueprint, request
from app.helpers import (get_cnt_of_active_members_in_past,
                         get_cnt_of_new_members_in_past,
                         get_cnt_of_leave_members_in_past,
                         get_all_hub_plans_of_plan_type,
                         get_all_member_reports_of_hub_plans)
from flask.ext.api import status
from app.models import PLAN_TYPES, Hub
from collections import OrderedDict

# create blueprint instance
mod = Blueprint('main', __name__, url_prefix='/api')


# create views here
@mod.route("/cards", methods=['GET'])
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
    new_members_in_past_months = get_cnt_of_new_members_in_past(days=30)

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
    new_members_in_past_weeks = get_cnt_of_new_members_in_past(days=7)

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
    leave_members_in_past_weeks = get_cnt_of_leave_members_in_past(days=7)

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


@mod.route("/reports", methods=['GET'])
def get_reports():
    # extract hub_name` argument from request
    hub_name = request.args.get('hub_name', None)

    #  extract plan_type
    plan_type = request.args.get('plan_type', None)

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

    # intializise list to have results to return as response
    res = list()

    # get all hub plans for all above plans
    hub_plans = get_all_hub_plans_of_plan_type(hub, plan_type)

    # get member report's for all hub_plan's
    m_reports = get_all_member_reports_of_hub_plans(hub_plans)

    # serialize all member report's and append to them in result
    for mr in m_reports:
        res.append(mr.serialize())

    return res
