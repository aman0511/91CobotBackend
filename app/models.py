# Models for app
from app import db
from app.utils import get_current_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), index=True, unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


class Hub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    location = db.Column(db.String(100))

    def __init__(self, name, location):
        self.name = name
        self.location = location

    def get_dict(self):
        return {'name': self.name, 'location': self.location}

    def __repr__(self):
        return '<Hub %s>' % (self.name)


class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    price = db.Column(db.Numeric(precision=10, scale=4))

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_dict(self):
        return {'name': self.name, 'total_price_per_cycle': self.price}

    def __repr__(self):
        return '<Plan %s>' % (self.name)


class HubPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'))
    hub = db.relationship('Hub',
                          backref=db.backref('hub_plan_set', lazy='dynamic'))

    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    plan = db.relationship('Plan',
                           backref=db.backref('hub_plan_set', lazy='dynamic'))

    def __init__(self, hub, plan):
        self.hub = hub
        self.plan = plan

    def __repr__(self):
        return '<HubPlan %s %s>' % (self.hub.name, self.plan.name)


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cobot_id = db.Column(db.String(50), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
                           backref=db.backref('membership', lazy='dynamic'))
    plans = db.relationship('MembershipPlan',
                            backref=db.backref('membership'), lazy='dynamic',
                            order_by='MembershipPlan.start_date')

    confirmed_at = db.Column(db.Date, index=True)
    canceled_to = db.Column(db.Date, index=True)

    def __init__(self, cb_id, user, confirmed_at, canceled_to=None):
        self.cobot_id = cb_id
        self.user = user
        self.confirmed_at = confirmed_at
        if (canceled_to or canceled_to != 'null'):
            self.canceled_to = canceled_to
        else:
            self.canceled_to = 'null'

    def __repr__(self):
        return '<Membership %s %s>' % (self.cobot_id, self.user)


class MembershipPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hub_plan_id = db.Column(db.Integer, db.ForeignKey('hub_plan.id'))
    hub_plan = db.relationship('HubPlan',
                               backref=db.backref('membership_plan_set',
                                                  lazy='dynamic'))
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'))
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)

    def __init__(self, membership, hub_plan, end_date=None):
        self.membership = membership
        self.hub_plan = hub_plan
        self.start_date = get_current_date()
        if (end_date or end_date != 'null'):
            self.end_date = end_date
        else:
            self.end_date = 'null'

    def __repr__(self):
        return '<MembershipPlan %s %s>' % (self.membership, self.hub_plan)


class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    date = db.Column(db.Date, index=True)

    def __init__(self, date):
        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day

    def __repr__(self):
        return '<Time %s>' % (self.date)


class MemberReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_id = db.Column(db.Integer, db.ForeignKey('time.id'))
    time = db.relationship('Time',
                           backref=db.backref('member_report_set',
                                              lazy='dynamic'))
    hub_plan_id = db.Column(db.Integer, db.ForeignKey('hub_plan.id'))
    hub_plan = db.relationship('HubPlan',
                               backref=db.backref('member_report_set',
                                                  lazy='dynamic'))
    new_member_count = db.Column(db.Integer, default=0)
    retain_member_count = db.Column(db.Integer, default=0)
    leave_member_count = db.Column(db.Integer, default=0)

    def __init__(self, time, hub_plan):
        self.time = time
        self.hub_plan = hub_plan

    def __repr__(self):
        return '<MemberReport %s %s>' % (self.hub_plan, self.time)

    def increment_nm_cnt_by(self, cnt):
        self.new_member_count += cnt

    def increment_rm_cnt_by(self, cnt):
        self.retain_member_count += cnt

    def increment_lm_cnt_by(self, cnt):
        self.leave_member_count += cnt
