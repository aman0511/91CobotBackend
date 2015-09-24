from flask import url_for
from app import db, app, models
from app.utils import get_date

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename=filename)
)


# Database Models related helpers methods
def add_to_db_session(items):
    """
    Add items to db session
    """
    for item in items:
        try:
            if item:
                db.session.add(item)
            else:
                print 'Item not found'
        except Exception:
            raise


def commit_to_db():
    """
    Commit all updates/changes to DB
    """
    try:
        db.session.commit()
    except Exception:
        raise


def create_hub(hub_data):
    """
    Create a new hub instance of a Hub table
    """
    if 'name' in hub_data and 'location' in hub_data:
        return models.Hub(hub_data['name'], hub_data['location'])
    else:
        None


def get_hub(hub_data):
    """
    Get a hub instance from a Hub table
    """
    return models.Hub.query.filter_by(name=hub_data['name']).first()


def is_hub_exists(hub_data):
    """
    Checks whether hub exists or not in a Hub table
    """
    if get_hub(hub_data):
        return True
    else:
        return False


def create_or_get_hub(data):
    """
    Create if hub not exist otherwise return hub instance of a Hub
    table
    """
    if is_hub_exists(data):
        return get_hub(data)
    else:
        return create_hub(data)


def create_user(user_data):
    """
    Create a new user instance of a User table
    """
    if 'name' in user_data and 'email' in user_data:
        return models.User(user_data['name'], user_data['email'])
    else:
        None


def get_user(data):
    """
    Get a user instance from a User table
    """
    return models.User.query.filter_by(email=data['email']).first()


def is_user_exists(user_data):
    """
    Checks whether user exists or not in a User table
    """
    if get_user(user_data):
        return True
    else:
        return False


def create_or_get_user(data):
    """
    Create if user not exist otherwise return user instance of a User
    table
    """
    if is_user_exists(data):
        return get_user(data)
    else:
        return create_user(data)


def create_plan(plan_data):
    """"
    Create a plan instance of a Plan table
    """
    if 'name' in plan_data and 'total_price_per_cycle' in plan_data:
        return models.Plan(plan_data['name'].strip(),
                           plan_data['total_price_per_cycle'])
    else:
        None


def get_plan(data):
    """
    Get a plan instance from a Plan table
    """
    return models.Plan.query.filter_by(name=data['name'].strip()).first()


def is_plan_exists(plan_data):
    """
    Checks whether plan exists or not in a Plan table
    """
    if get_plan(plan_data):
        return True
    else:
        return False


def is_new_plan(plan):
    """
    Checks whether a plan is new or not (i.e plan instance have
    id field set or not)
    """
    return False if plan.id else True


def create_or_get_plan(data):
    """
    Create if plan not exist otherwise return plan instance from a Plan table
    """
    if is_plan_exists(data):
        return get_plan(data)
    else:
        return create_plan(data)


def create_hub_plan(hub, plan):
    """
    Create a hub_plan instance of a HubPlan table
    """
    if hub and plan:
        return models.HubPlan(hub, plan)
    else:
        None


def get_hub_plan(hub_data, plan_data):
    """
    Get a hub_plan instance from a HubPlan table
    """
    hub = get_hub(hub_data)
    plan = get_plan(plan_data)
    return models.HubPlan.query.filter_by(hub=hub, plan=plan).first()


def get_hub_plan_from_instances(hub, plan):
    """
    Get a hub_plan instance from a HubPlan table using Hub table instance and
    Plan table instance
    """
    return models.HubPlan.query.filter_by(hub=hub, plan=plan).first()


def is_hub_plan_exists(hub_data, plan_data):
    """
    Checks whether a hub_plan instance exists or not in a HubPlan table
    """
    if get_hub_plan(hub_data, plan_data):
        return True
    else:
        return False


def create_or_get_hub_plan(hub_data, plan_data):
    """
    Create if hub_plan not exist otherwise return hub_plan instance from a
    HubPlan table
    """
    if is_hub_plan_exists(hub_data, plan_data):
        return get_hub_plan(hub_data, plan_data)
    else:
        hub = get_hub(hub_data)
        plan = get_plan(plan_data)
        return create_hub_plan(hub, plan)


def create_membership(membership_data, user):
    """
    Create a membership instance of a Membership table
    """
    if 'id' in membership_data and 'confirmed_at' in membership_data and \
            'canceled_to' in membership_data:
            return models.Membership(membership_data['id'], user,
                                     get_date(membership_data['confirmed_at']),
                                     get_date(membership_data['canceled_to']))
    else:
        None


def get_membership(data):
    """
    Get a membership instance from a Membership table
    """
    return models.Membership.query.filter_by(cobot_id=data['id']).first()


def is_membership_exists(membership_data):
    """
    Checks whether a membership exists or not in a Membership table
    """
    if get_membership(membership_data):
        return True
    else:
        return False


def is_new_membership(membership):
    """
    Checks whether a membership is new or not (i.e membership instance have
    id field set or not)
    """
    return False if membership.id else True


def create_or_get_membership(membership_data, user):
    """
    Create if membership not exist otherwise return membership instance of a
    Membership table
    """
    if is_membership_exists(membership_data):
        return get_membership(membership_data)
    else:
        return create_membership(membership_data, user)


def create_membership_plan(membership, hub_plan, end_date=None):
    """
    Create a membership_plan instance of a MembershipPlan table
    """
    return models.MembershipPlan(membership, hub_plan, end_date)


def get_last_plan_of_membership(membership):
    """
    Get a last plan of a membership if any, otherwise None
    """
    return membership.plans.all()[-1] if len(membership.plans.all()) > 0 \
        else None


def is_membership_plan_changed(membership, hub_plan):
    """
    Check if a plan of a membership changed or not
    """
    if membership and hub_plan:
        last_membership_plan = get_last_plan_of_membership(membership)

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
    if end_date and membership:
        last_membership_plan = get_last_plan_of_membership(membership)
        if last_membership_plan:
            last_membership_plan.end_date = end_date
            return last_membership_plan
        else:
            None
    else:
        None
