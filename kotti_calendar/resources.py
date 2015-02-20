# -*- coding: utf-8 -*-

from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Document
from kotti.sqla import JsonType
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from zope.interface import implements

from kotti import Base

from kotti_calendar import _


other_calendars_association_table = Table(
    'other_calendars_assocation',
    Base.metadata,
    Column('calendar_id', Integer, ForeignKey('calendars.id')),
    Column('event_id', Integer, ForeignKey('events.id')),
)


class Calendar(Document):
    """ A calendar is a container for events. """

    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    feeds = Column(JsonType(), nullable=False)
    weekends = Column(Boolean())

    type_info = Document.type_info.copy(
        name=u'Calendar',
        title=_(u'Calendar'),
        add_view=u'add_calendar',
        addable_to=[u'Document'],
        )

    def __init__(self, feeds=(), weekends=True, **kwargs):
        super(Calendar, self).__init__(**kwargs)
        self.feeds = feeds
        self.weekends = weekends


class Event(Document):
    """ Events are documents with start and optional end datetime. """

    implements(IDefaultWorkflow)

    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    start = Column('start', DateTime(), nullable=False)
    end = Column('end', DateTime())
    all_day = Column('all_day', Boolean())
    link_to_file = Column('link_to_file', Boolean())

    other_calendars = relationship(
        "Calendar",
        secondary=other_calendars_association_table,
    )

    type_info = Document.type_info.copy(
        name=u'Event',
        title=_(u'Event'),
        add_view=u'add_event',
        addable_to=[u'Calendar'],
        )

    def __init__(self, start=None, end=None, all_day=False, link_to_file=False,
                 other_calendar_list=None, other_calendar_id_list=None,
                 in_navigation=False, **kwargs):

        super(Event, self).__init__(in_navigation=in_navigation, **kwargs)

        self.start = start
        self.end = end
        self.all_day = all_day
        self.link_to_file = link_to_file

        self.other_calendars = Event._setup_other_calendars(
            other_calendar_list,
            other_calendar_id_list
        )

    @staticmethod
    def _setup_other_calendars(cal_list, cal_id_list):
        """
        Argument parsing method (convenience) for other_calendar_list

        Supplied with either a list of calendars or a list of calendar ids,
        this method ensures that a list of calendars is returned.

        If all arguments evaluate to False, an empty list is returned.

        :param list cal_list: list of calendars
        :param list calendar_id: list of calendar ids
        :returns: list of calendars
        """
        if cal_list:
            return cal_list

        if not cal_id_list:
            return []

        return [
            Calendar.query.get(calendar_id)
            for calendar_id in cal_id_list
            ]
