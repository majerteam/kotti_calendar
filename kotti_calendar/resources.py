from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Table
from sqlalchemy.orm import relationship
from zope.interface import implements

from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from kotti.resources import Document
from kotti.sqla import JsonType
from kotti import Base

from kotti_calendar import _


other_calendars_association_table = Table(
    'other_calendars_assocation',
    Base.metadata,
    Column('calendar_id', Integer, ForeignKey('calendars.id')),
    Column('event_id', Integer, ForeignKey('events.id')),
)


class Calendar(Content):
    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)
    feeds = Column(JsonType(), nullable=False)
    weekends = Column(Boolean())

    type_info = Content.type_info.copy(
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
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    start = Column('start', DateTime(), nullable=False)
    end = Column('end', DateTime())
    all_day = Column('all_day', Boolean())

    other_calendars = relationship(
        "Calendar",
        secondary=other_calendars_association_table,
    )

    type_info = Content.type_info.copy(
        name=u'Event',
        title=_(u'Event'),
        add_view=u'add_event',
        addable_to=[u'Calendar'],
        )

    def __init__(self, start=None, end=None, all_day=False,
                 in_navigation=False, other_calendar_list=(),
                 other_calendar_id_list=(), **kwargs):
        super(Event, self).__init__(in_navigation=in_navigation, **kwargs)
        self.start = start
        self.end = end
        self.all_day = all_day
        if other_calendar_list:
            self.other_calendars = other_calendar_list
        elif other_calendar_id_list:
            self.other_calendars = []
            for calendar_id in other_calendar_id_list:
                calendar = Calendar.query.get(calendar_id)
                self.other_calendars.append(calendar)
        else:
            self.other_calendars = []
