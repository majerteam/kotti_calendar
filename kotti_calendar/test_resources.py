import kotti_calendar.resources


class DummyCal(object):
    """
    Simple mock calendar.
    """
    def __init__(self, oid):
        self.id = oid


def _make_a_calendar_idlist(cal_list):
    """
    returns a list of calendar ids

    Convenience function

    :param cal_list: list of calendars
    """
    return [cal.id for cal in cal_list]


class TestMultiCalEvent:
    #calendars number generated at each _make_a_calendar_list call
    _CAL_GENERATED_NB = 10
    _OFFSET = 0

    def _make_a_calendar_list(self):
        """
        returns a list of new calendars

        Incrementing _OFFSET guaranties no calendar has own id
        """
        TestMultiCalEvent._OFFSET += self._CAL_GENERATED_NB
        return [
            DummyCal(oid)
            for oid in xrange(
                TestMultiCalEvent._OFFSET,
                TestMultiCalEvent._OFFSET + self._CAL_GENERATED_NB
            )
            ]


    def setup_method(self, method):
        self.other_cals = self._make_a_calendar_list()

        self.backup_cal_query = kotti_calendar.resources.Calendar.query
        kotti_calendar.resources.Calendar.query = dict(
            (cal.id, cal)
            for cal in self.other_cals
        )

    def teardown_method(self, method):
        self.other_cals = []
        kotti_calendar.resources.Calendar.query = self.backup_cal_query


    def test_multi_cal_list(self):
        """
        Test that we can build an event in several calendars from a calendar
        list
        """

        event = kotti_calendar.resources.Event(
            other_calendar_list=self.other_cals
        )

        assert set(self.other_cals) == set(event.other_calendars)

    def test_multi_calid_list(self):
        """
        Test that we can build an event in several calendars from a calendars ID
        list
        """
        other_calids = _make_a_calendar_idlist(self.other_cals)

        event = kotti_calendar.resources.Event(
            other_calendar_id_list=other_calids
        )

        assert set(self.other_cals) == set(event.other_calendars)

    def test_multi_cal_no_othercals(self):

        event = kotti_calendar.resources.Event()
        assert event.other_calendars == []

    def test_multi_cal_toomuchinfo(self):
        """
        Tests that other_calendar_list has precedence over
        other_calendar_id_list
        """
        more_calendars = self._make_a_calendar_list()
        more_calendars_ids = _make_a_calendar_idlist(more_calendars)
        event = kotti_calendar.resources.Event(
            other_calendar_list=self.other_cals,
            other_calendar_id_list=more_calendars_ids
        )
        assert set(self.other_cals) == set(event.other_calendars)
        assert all(cal not in event.other_calendars for cal in more_calendars)
