# -*- coding: utf-8 -*-
"""
A model mixin class have some basic functions which provide extra
functionality to model class
"""
import traceback
from app import db
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.ext.declarative import DeclarativeMeta


class ModelMixin(object):
    """
    Defines the general purpose functions for models
    """
    # sqlalchemy database application instance
    __db__ = db

    def __init__(self, *args, **kwargs):
        """
        Instantiates the base class object for error dictionary
        """
        # set all given attributes of model
        self._set_fields(**kwargs)

        # initialize errors dictionary
        self.errors = dict()

    @property
    def __columns__(self):
        """
        Set property contains all names of columns of a model
        """
        return [m.key for m in self.__table__.columns]

    @property
    def __relationships__(self):
        """
        Set property contains all names of direct relationships(i.e not
        contains backref named attribute) of a model
        """
        back_ref_relationships = list()
        items = self.__mapper__.relationships.items()
        for (key, value) in items:
            if isinstance(value.backref, tuple):
                back_ref_relationships.append(key)
        return back_ref_relationships

    @property
    def __fields__(self):
        """
        Set property contains fields to be used during serialize or deserialize
        """
        fields = getattr(self.__class__, '__fields__', [])
        if isinstance(fields, property):
            return self.__columns__
        return fields

    def _is_process_field(self, field):
        """
        Checks whether field is in process fields list or not
        """
        if field in self.__fields__:
            return True
        return False

    def _set_fields(self, **kwargs):
        """
        Set all valid attributes of a object which are passed
        """
        # remove id field, if any
        kwargs.pop('id', None)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def _serialize_column(self, key, **kwargs):
        """
        Serialize a single column of a model depending upon it's type
        """
        obj = getattr(self, key)
        if isinstance(obj, (datetime, date)):
            # column is of datetime or date type
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            # column is of Decimal type
            return obj.to_eng_string()
        else:
            return obj

    def _serialize_columns(self, **kwargs):
        """
        Serialize all columns in a process_fields of a model
        """
        res = dict()
        for c in self.__columns__:
            if self._is_process_field(c):
                res[c] = self._serialize_column(c)
        return res

    def _serialize_relationship(self, key, **kwargs):
        """
        Serialize a single relationship of a model depending upon it's type
        """
        obj = getattr(self, key)
        if isinstance(obj.__class__, DeclarativeMeta):
            # if relationship contains single item(i.e One-to-Many or
            # One-to-One)
            return obj.serialize(**kwargs)
        else:
            # else relationship contains a list of items(i.e Many-to-Many or
            # Many-to-One)
            res = list()
            objects = getattr(self, key).all()
            for obj in objects:
                res.append(obj.serialize())
            return res

    def _serialize_relationships(self, **kwargs):
        """
        Serialize all relationships in a process_fields of a model
        """
        res = dict()
        for r in self.__relationships__:
            if self._is_process_field(r):
                res[r] = self._serialize_relationship(r)
        return res

    def serialize(self, relationships=True, **kwargs):
        """
        Serialize a model instance support nested relationships also
        """
        res = dict()
        # serialize data of native columns of model
        res.update(self._serialize_columns(**kwargs))

        if relationships:
            # serialize data of relationships columns of model
            res.update(self._serialize_relationships(**kwargs))
        return res

    @classmethod
    def deserialize(cls, **data):
        """
        Deserialize data into model attributes and return it's instance
        :parm data(dict): contains all the fields that will be updated
         for the entity as keys
        return: Entity object crosspoding to given id
        """
        return cls()._set_fields(**data)

    @classmethod
    def _filter_by(cls, **kwargs):
        """
        Return a filtered results
        :param **kwargs: filter parameters
        """
        try:
            return cls.query.filter_by(**kwargs)
        except Exception, e:
            raise e

    @classmethod
    def find(cls, serialize=False, **kwargs):
        """
        Returns a list of instances filtered by the specified keyword
        arguments.
        :param **kwargs: filter parameters
        """
        try:
            return cls._filter_by(**kwargs).all()
        except Exception, e:
            raise e

    @classmethod
    def first(cls, **kwargs):
        """
        Returns the first instance found of the service's model filtered
        by the specified key word arguments.
        :param **kwargs: filter parameters
        """
        try:
            return cls._filter_by(**kwargs).first()
        except:
            return None

    @classmethod
    def get(cls, **kwargs):
        """
        Returns the first instance found of the service's model filtered
        by the specified key word arguments.
        :param **kwargs: filter parameters
        """
        return cls.first(**kwargs)

    @classmethod
    def get_all(cls, **kwargs):
        """
        Returns a list of all instances
        """
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id, **kwargs):
        """
        Returns model instance of given id
        :parm id: id of the requested model
        return: model instance crosspoding to given id
        """
        return cls.first(**{'id': id})

    @classmethod
    def new(cls, **kwargs):
        """
        Returns a new, unsaved instance of the service's model class.
        :param **kwargs: instance parameters
        """
        return cls.deserialize(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        """
        Returns a new, saved instance of the service's model class.
        :param **kwargs: instance parameters
        """
        return cls.new(**kwargs).save()

    @classmethod
    def is_exists(cls, **kwargs):
        """
        Checks whether instance exists or not in a database
        """
        if cls.get(**kwargs):
            return True
        else:
            return False

    @classmethod
    def create_or_get(cls, save=True, **kwargs):
        """
        Create if instance not exists otherwise return an instance of a
        model
        """
        if cls.is_exists(**kwargs):
            return cls.get(**kwargs)
        else:
            return cls.create(**kwargs) if save else cls.new(**kwargs)

    @classmethod
    def _add(cls, obj):
        """
        Add to database session
        """
        try:
            cls.__db__.session.add(obj)
        except Exception:
            traceback.print_exc()
        return obj

    @classmethod
    def _delete(cls, obj):
        """
        Add to database session
        """
        try:
            cls.__db__.session.delete(obj)
        except Exception:
            traceback.print_exc()
        return obj

    @classmethod
    def commit(cls):
        """
        Commit all pending changes to database
        """
        try:
            cls.__db__.session.commit()
        except Exception:
            traceback.print_exc()
        return None

    def save(self):
        """
        Commits the model to the database and returns the model
        :param model: the model to save
        """
        self.__class__._add(self)
        self.__class__.commit()
        return self

    def clone(self, save=False, **kwargs):
        """
        Clone the models and create a new instance
        """
        data = self.serialize(relationships=False, **kwargs)
        return self.__class__.new(**data) if save else \
            self.__class__.create(**data)

    def update(self, **kwargs):
        """
        Returns an updated instance of the service's model class.
        :param model: the model to update
        :param **kwargs: update parameters
        """
        self._set_fields(**kwargs)
        self.save()
        return self

    @classmethod
    def delete_item(cls, instance, **kwargs):
        """
        Delete a passed single instance from a database
        """
        cls._delete(instance)
        cls.commit()

    @classmethod
    def delete_by_id(cls, id, **kwargs):
        """
        Immediately deletes the specified model instance.
        :param id: id of the model instance to delete
        """
        # get model instace by id
        instance = cls.get_by_id(id)
        cls.delete_item(instance)
        return None

    @classmethod
    def delete_items(cls, instances_list, **kwargs):
        """
        Delete all model instance passed in a list from database
        """
        for instance in instances_list:
            cls.delete_item(instance)
