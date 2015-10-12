# -*- coding: utf-8 -*-
from datetime import date
from app import db
from app.mixins import ModelMixin

# a types of plan
PLAN_TYPES = ('Full Time', 'Part Time', 'Others', 'Ignore')


class User(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    email = db.Column(db.String(100), index=True)

    __fields__ = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<User %r>' % (self.name)


class Location(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)

    __fields__ = ['name']

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Location %s>' % (self.name)


class Hub(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location',
                               backref=db.backref('hub_set', lazy='dynamic'))

    __fields__ = ['name', 'location']

    def __init__(self, *args, **kwargs):
        super(Hub, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Hub %s %s>' % (self.name, self.location)


class Plan(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    type = db.Column(db.Enum(PLAN_TYPES, name='plan_types'))
    price = db.Column(db.Numeric(precision=20, scale=4))

    __fields__ = ['type', 'name', 'price']

    def __init__(self, *args, **kwargs):
        super(Plan, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Plan %s>' % (self.name)


class HubPlan(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'))
    hub = db.relationship('Hub',
                          backref=db.backref('hub_plan_set', lazy='dynamic'))

    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    plan = db.relationship('Plan',
                           backref=db.backref('hub_plan_set', lazy='dynamic'))

    __fields__ = ['hub', 'plan']

    def __init__(self, *args, **kwargs):
        super(HubPlan, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<HubPlan %s %s>' % (self.hub.name, self.plan.name)


class Membership(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cobot_id = db.Column(db.String(50), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hub_id = db.Column(db.Integer, db.ForeignKey('hub.id'))
    user = db.relationship('User',
                           backref=db.backref('membership', lazy='dynamic'))
    hub = db.relationship('Hub',
                          backref=db.backref('membership', lazy='dynamic'))
    plans = db.relationship('MembershipPlan',
                            backref=db.backref('membership'), lazy='dynamic',
                            order_by='MembershipPlan.start_date')

    confirmed_at = db.Column(db.Date, index=True)
    canceled_to = db.Column(db.Date, index=True)

    __fields__ = ['cobot_id', 'user', 'plans', 'confirmed_at', 'canceled_to']

    def __init__(self, *args, **kwargs):
        super(Membership, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Membership %s %s>' % (self.cobot_id, self.user)

    def assign_hub(self, hub):
        """
        Assign a hub to membership
        """
        if isinstance(hub, Hub):
            self.hub = hub
            self.save()

    def assign_user(self, user):
        """
        Assign a user to membership
        """
        if isinstance(user, User):
            self.user = user
            self.save()

    def set_canceled_date(self, c_date):
        """
        Set a canceled_to date of membership and also set end_date of last
        membership_plan of this membership as c_date
        """
        if isinstance(c_date, date):
            self.canceled_to = c_date
            last_membership_plan = self.get_last_membership_plan()
            if last_membership_plan:
                self.last_membership_plan.end_date = c_date
            self.save()

    def get_last_membership_plan(self):
        """
        Return a last membership_plan instance
        """
        if getattr(self, 'last_membership_plan', None):
            # if last_membership_plan attribute is set then return it
            return self.last_membership_plan

        # otherwise, get it from database, set attribute and return it
        m_plans = self.plans.all()
        self.last_membership_plan = m_plans[-1] if len(m_plans) > 0 else None
        return self.last_membership_plan


class MembershipPlan(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hub_plan_id = db.Column(db.Integer, db.ForeignKey('hub_plan.id'))
    hub_plan = db.relationship('HubPlan',
                               backref=db.backref('membership_plan_set',
                                                  lazy='dynamic'))
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'))
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)

    __fields__ = ['hub_plan', 'membership', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        super(MembershipPlan, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<MembershipPlan %s %s>' % (self.membership, self.hub_plan)

    def set_end_date(self, e_date):
        """
        Set end_date of membership plan
        """
        if isinstance(e_date, date):
            self.end_date = e_date
            self.save()


class Time(ModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    date = db.Column(db.Date, index=True)

    __fields__ = ['year', 'month', 'date']

    def __init__(self, *args, **kwargs):
        super(Time, self).__init__(*args, **kwargs)
        if self.date:
            self.year = self.date.year
            self.month = self.date.month
        self.save()

    def __repr__(self):
        return '<Time %s>' % (self.date)


class MemberReport(ModelMixin, db.Model):
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
    new_member_revenue = db.Column(db.Numeric(precision=20, scale=4),
                                   default=0)
    retain_member_revenue = db.Column(db.Numeric(precision=20, scale=4),
                                      default=0)
    leave_member_revenue = db.Column(db.Numeric(precision=20, scale=4),
                                     default=0)

    __fields__ = ['hub_plan', 'time', 'new_member_count',
                  'retain_member_count', 'leave_member_count',
                  'new_member_revenue', 'retain_member_revenue',
                  'leave_member_revenue']

    def __init__(self, *args, **kwargs):
        super(MemberReport, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<MemberReport %s %s>' % (self.hub_plan, self.time)

    def reset_all_counter(self):
        self.new_member_count = 0
        self.retain_member_count = 0
        self.leave_member_count = 0
        self.new_member_revenue = 0
        self.retain_member_revenue = 0
        self.leave_member_revenue = 0

    def increment_nm_cnt_by(self, cnt):
        self.new_member_count += cnt

    def increment_rm_cnt_by(self, cnt):
        self.retain_member_count += cnt

    def increment_lm_cnt_by(self, cnt):
        self.leave_member_count += cnt

    def increment_nm_rev_by(self, cnt):
        self.new_member_revenue += cnt

    def increment_rm_rev_by(self, cnt):
        self.retain_member_revenue += cnt

    def increment_lm_rev_by(self, cnt):
        self.leave_member_revenue += cnt
