# coding=utf-8
"""
date_time_tools
===============
"""
from typing import Union
import datetime
import DateTime
import pendulum
from dateutil.parser import parse
from dateutil.parser._parser import ParserError


TIME_ELS = ('h', 'm', 's', 'ms')

time_dividers = {
    'h': 1/24,
    'm': 1/24/60,
    's': 1/24/60/60,
    'ms': 1/24/60/60/1000
}


def is_valid_datetime_string(
    datestring: str,
    returning: str = None
) -> bool:
    """Check for the validity of a date/time string

    This function is only a wrapper for str_to_dt.

    There a some fundamental assumptions:
    - dates specified with hyphens or slashes are only valid with the year in the first place
    - dates with dots are only valid with the day in the first place

    The dates are parsed according to the above-mentioned assumptions, if there is
    a conflict with 4-digit year values, it is considered invalid

    :param returning: can return a tuple

    .. note:: This does not work with ISO8601 strings! (returns False)
    """
    return str_to_dt(
        datestring=datestring,
        checkonly=True,
        returning=returning
    )


def get_dateformat(
    datestring: str,
    checkonly: bool = False,
    leading_zeroes: bool = True,
    for_DateTime: bool = False
) -> str:
    """Get the format string needed to convert a datetime string to an object

    :param checkonly: if the datestring is invalid, return False instead of raising an error
    :todo: times!
    :raises ValueError: if an invalid datetime or DateTime string is provided
    """
    # first let's check for ISO8601 strings
    if checkonly:
        try:
            pendulum.parse(datestring)
            return True
        except pendulum.parsing.exceptions.ParserError:
            pass  # don't return False, because it may be a valid date string

    timefmt = ''
    if ' ' in datestring:
        try:
            datestring, timestring = datestring.split()
        except ValueError:
            raise ValueError(f'{datestring} is not a valid date or datetime string.')

        colon_count = timestring.count(':')
        timefmt = ' %H:%M'
        if colon_count == 2:
            timefmt += '%S'
        elif colon_count > 2:
            raise ValueError(f'{datestring} is not a valid date or datetime string.')

    if '.' in datestring:  # international format
        datefmt = '%d.%m.%Y'

    elif '/' in datestring:
        if len(datestring.split('/')[0]) < 3:
            if for_DateTime:
                datefmt = 'us'
            else:
                datefmt = '%m/%d/%Y'  # US format
        else:
            if for_DateTime:
                datefmt = 'international'
            else:
                datefmt = '%Y/%m/%d'  # international format
    elif '-' in datestring:  # international format
        if for_DateTime:
            datefmt = 'international'
        else:
            datefmt = '%Y-%m-%d'
    else:  # default
        if for_DateTime:
            datefmt = 'international'
        else:
            datefmt = '%d.%m.%Y'

    if for_DateTime:
        try:
            DateTime.DateTime(datestring, datefmt=datefmt)
        except DateTime.interfaces.DateError:
            if checkonly:
                return False
            raise ValueError(f'{datestring} is not a valid date or datetime string.')
    else:
        try:
            datetime.datetime.strptime(datestring, datefmt)
        except ValueError:
            if checkonly:
                return False
            raise ValueError(f'{datestring} is not a valid date or datetime string.')

        if not leading_zeroes:
            datefmt = datefmt.replace(
                '%d', '%-d'
            ).replace('%m', '%-m')

    if checkonly:
        return True
    return datefmt + timefmt


def str_to_dt(
    datestring: str,
    fmt: str = None,
    checkonly: bool = False,
    returning: str = None
) -> datetime.datetime:
    """ Convert a string to datetime.datetime

    This function is also used to evaluate the validity of a date/time string

    :param fmt: default: %d.%m.%Y
    :param checkonly: returns False if the date/time string is not valid
    :param returning: only value: 'tuple' (only in conjunction with checkonly)
    """

    if not fmt:
        naked_date = datestring.split()[0]
        point_notation = True if '.' in naked_date else False
        hyphen_notation = True if '-' in naked_date else False
        slash_notation = True if '/' in naked_date else False

        if (
                (
                    point_notation
                    or hyphen_notation
                    or slash_notation
                )  # otherwise it may be just a time string
                and (
                    point_notation
                    and len(naked_date.split('.')[0]) > 2
                )
                or (
                    hyphen_notation
                    and len(naked_date.split('-')[-1]) > 2
                )
                or (
                    slash_notation
                    and len(naked_date.split('/')[-1]) > 2
                )
        ):
            if checkonly:
                return False
            else:
                raise Exception(f'invalid date string {datestring}')

        try:
            dt = parse(
                datestring,
                dayfirst=point_notation,
                yearfirst=hyphen_notation or slash_notation
            )
        except ParserError as e:
            if checkonly:
                if returning == 'tuple':
                    return (False, e)
                return False
            else:
                raise ParserError(e)
        if checkonly:
            if returning == 'tuple':
                return (True, None)
            else:
                return True
        return dt
    else:
        return datetime.datetime.strptime(datestring, fmt)


def str_to_DT(
    datestring: str,
    fmt: str = None
) -> DateTime.DateTime:
    """ Convert a string to Datetime.Datetime

    The conversion is made with datetime.datetime first, because
    DateTime.DateTime cannot convert a string with a given format-string

    :param fmt: default: %d.%m.%Y
    """
    if not fmt:
        return DateTime.DateTime(
            str_to_dt(datestring)
        )
    else:
        return DateTime.DateTime(
            str_to_dt(
                datestring=datestring,
                fmt=fmt
            )
        )


def str_to_pendulum(
    datestring: str,
    fmt: str = None
) -> pendulum.DateTime:
    """ Convert a string to pendulum.DateTime

    :param fmt: default: %d.%m.%Y (if not specified, the datestring is assumed to be valid ISO8601)
    """

    if not fmt:
        return pendulum.parse(datestring)
    else:
        return pendulum.from_format(datestring, fmt)


def str_to_date(
    datestring: str,
    fmt: str = None
) -> datetime.date:
    """ Convert a string to datetime.date

    :param fmt: default: %d.%m.%Y
    """

    if not fmt:
        return parse(
            datestring,
            dayfirst=True if '.' in datestring else False
        ).date()
    else:
        return datetime.datetime.strptime(datestring, fmt).date()


def DT_to_dt(
    DT: DateTime.DateTime
) -> datetime.datetime:
    """ Convert DateTime.DateTime to datetime.datetime """

    return datetime.datetime(
        DT.year(),
        DT.month(),
        DT.day(),
        DT.hour(),
        DT.minute()
    )


def DT_to_date(
    DT: DateTime.DateTime
) -> datetime.date:
    """ Convert DateTime.DateTime to datetime.date """
    return datetime.date(
        DT.year(),
        DT.month(),
        DT.day()
    )


def DT_to_pendulum(
    DT: DateTime.DateTime
) -> pendulum.DateTime:
    """ Convert DateTime.DateTime to pendulum.DateTime """

    tz = DT.timezone()

    offset = None

    if '+' in tz:
        offset = int(tz.split('+')[-1])
    elif '-' in tz:
        offset = - int(tz.split('-')[-1])
    
    if offset is not None:
        if not offset:
            tz = 'UTC'
        else:
            tz = pendulum.FixedTimezone(offset * 3600)
    else:
        tz = pendulum.timezone(tz)

    return pendulum.datetime(
        DT.year(),
        DT.month(),
        DT.day(),
        DT.hour(),
        DT.minute(),
        tz = tz
    )


def date_to_dt(
    date: datetime.date,
    H=None, M=None
) -> datetime.datetime:
    """ Convert datetime.date to datetime.datetime

    :param H: hour
    :param M: minute
    """

    if H and M:
        dt = datetime.datetime.combine(
            date,
            datetime.datetime(2000, 1, 1, int(H), int(M)).time()
        )
    else:
        dt = datetime.datetime.combine(
            date,
            datetime.datetime.min.time()
        )
    return dt


def date_to_DT(
    date: datetime.date
) -> DateTime.DateTime:
    """ Convert datetime.date to DateTime.DateTime

    :param fmt: default: %d.%m.%Y
    """

    return DateTime.DateTime(date_to_dt(date))


def dt_to_pendulum(
    dt: datetime.datetime
) -> pendulum.DateTime:
    """ Convert datetime.datetime to pendulum.DateTime """

    return pendulum.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute
    
    )


def pendulum_to_DT(
    pendulum_dt: pendulum.DateTime
) -> DateTime.DateTime:
    """ Convert pendulum.DateTime to DateTime.DateTime """

    return DateTime.DateTime(
        pendulum_dt.year,
        pendulum_dt.month,
        pendulum_dt.day,
        pendulum_dt.hour,
        pendulum_dt.minute
    ).toZone(pendulum_dt.timezone.name)


def convert_datetime(
    date: Union[
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime,
        pendulum.DateTime
    ],
    convert_to: str,
    fmt: str = None
) -> Union[datetime.datetime, datetime.date, DateTime.DateTime, str]:
    """ Conversion of date and time formats

    :param convertTo:

        - date: datetime.date
        - datetime: datetime.datetime
        - DateTime: DateTime.DateTime
        - str, string: string

    :param fmt: is used both for converting from and converting to
    """

    if isinstance(date, DateTime.DateTime):
        if convert_to == 'DateTime':
            return date
        elif convert_to == 'date':
            return DT_to_date(date)
        elif convert_to == 'datetime':
            return DT_to_dt(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
        elif convert_to == 'pendulum':
            return DT_to_pendulum(date)
    elif isinstance(date, pendulum.DateTime):
        if convert_to == 'datetime':
            return date
        elif convert_to == 'date':
            return date.date()
        elif convert_to == 'DateTime':
            return pendulum_to_DT(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
    elif isinstance(date, str):
        if convert_to in ('str', 'string'):
            if str_to_date(date, checkonly=True, fmt=fmt):
                return date
            else:
                raise Exception(f'{date} is not a valid date/time string!')
        elif convert_to == 'date':
            return str_to_date(date, fmt=fmt)
        elif convert_to == 'datetime':
            return str_to_dt(date, fmt=fmt)
        elif convert_to == 'DateTime':
            return str_to_DT(date, fmt=fmt)
        elif convert_to == 'pendulum':
            return pendulum.parse(date)
    elif isinstance(date, datetime.datetime):
        # datetime.datetime has to be checked BEFORE
        # datetime.date (isinstance(datetime.datetime, datetime.date) == True !)
        if convert_to == 'date':
            return date.date()
        elif convert_to == 'datetime':
            return date
        elif convert_to == 'DateTime':
            return DateTime.DateTime(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
        elif convert_to == 'pendulum':
            return dt_to_pendulum(date)
    elif type(date) is datetime.date:  # isinstance does not work
        if convert_to == 'date':
            return date
        elif convert_to == 'datetime':
            return date_to_dt(date)
        elif convert_to == 'DateTime':
            return date_to_DT(date)
        elif convert_to in ('str', 'string'):
            return date.strftime(fmt)
        elif convert_to == 'pendulum':
            return pendulum.datetime(
                date.year,
                date.month,
                date.day
            )


def get_calendar_week(
    date: Union[
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    ]
) -> int:
    """ Get calendard week (week nb of year) from a date

    :param date: can be any date, datetime, DateTime or string
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()[1]


def get_dow_number(
    date: Union[
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    ]
) -> int:
    """ Get day of week number from a date

    :param date: should be a datetime.date or a string formatted '%d.%m.%Y'
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()[2]


def get_isocalendar(
    date: Union[
        str,
        datetime.datetime,
        datetime.date,
        DateTime.DateTime
    ]
) -> datetime.date:
    """ Returns the isocalendar tuple: (year, woy, downb)

    Returns year, weeknb (week of year) and day of week number

    :param date: should be a datetime.date or a string formatted '%d.%m.%Y'
    """

    date = convert_datetime(date, 'date')

    return date.isocalendar()


def get_monday(
    year: int,
    week: int,
    endofweek: int = 7
) -> datetime.datetime:
    """ Returns monday as a datetime object

    .. warning:: obsolete!
    """

    year = int(year)
    week = int(week)
    endofweek = int(endofweek)

    if week < 1:
        first_monday_year = datetime.date.fromisocalendar(year, 1, 1)
        monday_back = first_monday_year - datetime.timedelta(weeks=abs(week))
        year, week, _ = monday_back.isocalendar()

    ref = datetime.date(year, 6, 6)
    ref_week, ref_day = ref.isocalendar()[1:]

    monday = ref + datetime.timedelta(days=7 * (week - ref_week) - ref_day + 1)

    return monday


def daterange_from_week(
    year: int,
    week: int,
    returning: str = 'date',
    endofweek: int = 7,
    fmt: str = '%d.%m.%Y'
) -> tuple:
    """Get a date range from a week

    :param returning:
           - DateTime
           - datetime (default)
           - date
           - pendulum
    :param fmt: default: '%d.%m.%Y'

    .. note:: Author: Andreas Bruhn, https://groups.google.com/forum/#!topic/de.comp.lang.python/p8LfbNMIJ5c

    .. note:: If weekday exceeds the year, then the date is from next year, even if the week is not correct then
    """
    monday = get_monday(
        year=year,
        week=week,
        endofweek=endofweek
    )

    last_day = monday + datetime.timedelta(days=endofweek - 1)

    monday = convert_datetime(monday, returning)
    last_day = convert_datetime(last_day, returning)

    return monday, last_day


def dates_from_week(
    year: int,
    week: int,
    returning: str = 'date',
    endofweek: int = 7,
    fmt: str = '%d.%m.%Y'
) -> list:
    """Get dates from a week

    .. note:: Author: Andreas Bruhn, https://groups.google.com/forum/#!topic/de.comp.lang.python/p8LfbNMIJ5c
    .. note:: If weekday exceeds the year, then the date is from next year, even if the week is not correct then

    :param returning:

        - DateTime (default)
        - datetime
        - date
        - pendulum

    :param fmt: default: '%d.%m.%Y'
    :param endofweek: 1 to 7 (monday to sunday)
    """

    monday = get_monday(
        year=year,
        week=week,
        endofweek=endofweek
    )

    dates = []

    for i in range(0, endofweek):
        dates.append(
            monday + datetime.timedelta(days=i)
        )

    # assert dates[0].isocalendar() == (int(year), int(week), 1)
    # assert dates[-1].isocalendar() == (int(year), int(week), int(endofweek))

    return_dates = []

    for date in dates:
        return_dates.append(
            convert_datetime(date, returning)
        )

    return return_dates


def day_from_week(
    year: int,
    week: int,
    weekday: int = 1,
    returning: str = 'date',
    fmt: str = '%d.%m.%Y'
) -> Union[datetime.datetime, datetime.date, DateTime.DateTime, pendulum.DateTime]:
    """Get day from a week

    :param weekday: begins with 1 = monday
    :param returning:

       - DateTime
       - datetime (default)
       - date
       - pendulum

    :param fmt: default: '%d.%m.%Y'
    """

    return dates_from_week(
        year=year,
        week=week,
        returning=returning,
        fmt=fmt
    )[int(weekday) - 1]


def monday_from_week(
    year: int,
    week: int,
    returning: str = 'date',
    fmt='%d.%m.%Y'
) -> Union[datetime.datetime, datetime.date, DateTime.DateTime, pendulum.DateTime]:
    """Get monday from a week

    :param: weekday begins with 1 = monday
    :param returning:

           - DateTime
           - datetime (default)
           - date

    :param fmt: default: '%d.%m.%Y'
    """

    return day_from_week(
        year=year,
        week=week,
        returning=returning,
        fmt=fmt
    )


def last_week_of_year(
    year: int
) -> int:
    """Get the last week of a year
    """
    last_week = datetime.date(year, 12, 28)
    return last_week.isocalendar()[1]


def remove_time(
    date_time: Union[datetime.datetime, DateTime.DateTime, pendulum.DateTime],
    returning: str = None
):
    """Remove time from a datetime or DateTime object

    :param date_time: must be a datetime or DateTime object
    :param returning: if None, the same type as date_time is returned,
            otherwise valid values are "datetime" and "DateTime"
    """
    if type(date_time) is datetime.date:
        return date_time
    elif isinstance(date_time, datetime.datetime):
        if not returning or returning == 'datetime':
            return datetime.datetime.combine(
                date_time,
                datetime.datetime.min.time()
            )
        elif returning == 'date':
            return date_time.date()
        elif returning == 'DateTime':
            return DateTime.DateTime(
                datetime.datetime.combine(
                    date_time,
                    datetime.min.time()
                )
            )
    elif isinstance(date_time, DateTime.DateTime):
        if not returning or returning == 'DateTime':
            return DateTime.DateTime(
                date_time.year(),
                date_time.month(),
                date_time.day()
            )
        elif returning == 'date':
            return datetime.datetime(
                date_time.year(),
                date_time.month(),
                date_time.day()
            ).date()
        elif returning == 'datetime':
            return datetime.datetime(
                date_time.year(),
                date_time.month(),
                date_time.day()
            )
    elif isinstance(date_time, pendulum.DateTime):
        if not returning or returning == 'pendulum':
            return date_time.start_of('day')
        elif returning == 'date':
            return date_time.date()
        elif returning == 'datetime':
            return date_time.datetime()
        elif returning == 'DateTime':
            return DateTime.DateTime(
                date_time.year,
                date_time.month,
                date_time.day
            )


def create_timedelta(
    timestr: str,
    dt: str
):
    """create a timedelta or a number from a time string

    :param timestr: format or H:M or H:M:S or H:M:S:ms, possibly with day: 4T03:12:31
    :param returningdt: dt, DT or pendulum
    """
    days_time = timestr.split('T')
    timestr = days_time[-1]
    days = 0
    if len(days_time) > 1:
        days = days_time[0]

    time_list = timestr.split(':')
    time_elements = {}

    for i, el in enumerate(TIME_ELS):
        try:
            time_elements[el] = int(time_list[i])
        except IndexError:
            time_elements[el] = 0

    if dt == 'datetime':
        t_delta = datetime.timedelta(
            days=days,
            hours=time_elements['h'],
            minutes=time_elements['m'],
            seconds=time_elements['s'],
            milliseconds=time_elements['ms'],
        )
    elif dt == 'DateTime':
        t_delta = days
        for el in TIME_ELS:
            t_delta += time_elements[el] * time_dividers[el]
    elif dt == 'pendulum':
        t_delta = pendulum.duration(
            days=days,
            hours=time_elements['h'],
            minutes=time_elements['m'],
            seconds=time_elements['s'],
            milliseconds=time_elements['ms'],
        )

    return t_delta


def add_time(
    date_time: Union[datetime.datetime, DateTime.DateTime, pendulum.DateTime],
    timestr: str,
    subtract: bool = False,
    returning: str = None
):
    """add or remove time from a datetime or DateTime object

    :param date_time: must be a datetime or DateTime object
    :param returning: if None, the same type as date_time is returned,
            otherwise valid values are "datetime" and "DateTime"

    We can safely assume that that the time string is in the format
    H:M or H:M:S or H:M:S:ms
    or
    dTH:M etc... (ex.: 4T03:12:31)
    """
    if subtract or timestr.startswith('-'):
        subtract = True
        timestr = timestr[1:]

    if isinstance(date_time, datetime.datetime):
        dt = 'datetime'
    elif isinstance(date_time, datetime.date):
        date_time = date_to_dt(date_time)
        dt = 'datetime'
    elif isinstance(date_time, DateTime.DateTime):
        dt = 'DateTime'
    elif isinstance(date_time, pendulum.DateTime):
        dt = 'pendulum'
    else:
        raise Exception('date_time has to be datetime.datetime, datetime.date or DateTime.DateTime!')

    t_delta = create_timedelta(
        timestr=timestr,
        dt=dt
    )

    if subtract:
        return date_time - t_delta
    else:
        return date_time + t_delta


def unravel_duration(
    duration: str,
    returning: str = 'list'
):
    """split a duration string into components

    duration comes in the format nTH:M:S:ms
    (days, hours, minutes, seconds, milliseconds)

    @param returning: list, tuple oder dictionary
    """
    if 'T' in duration:
        days, rest = duration.split('T')
        days = int(days)
    else:
        days = 0
        rest = duration

    elements = rest.split(':')

    hours = minutes = seconds = milliseconds = 0
    time_elements = [hours, minutes, seconds, milliseconds]

    for i, (element, time_measure) in enumerate(zip(elements, time_elements.copy())):
        time_elements[i] = int(element)

    time_elements.insert(0, days)

    for i, divider in zip(
        range(4, -1, -1),
        (1000, 60, 60, 24)
    ):
        time_element = int(time_elements[i] / divider)
        time_elements[i] -= time_element * divider
        time_elements[i - 1] += time_element

    if returning == 'list':
        return time_elements
    elif returning in ('dict', 'dictionary'):
        d = {}
        for name, val in zip(('days', 'hours', 'minutes', 'seconds', 'milliseconds'), time_elements):
            d[name] = val
        return d
    elif returning == 'tuple':
        tuple(time_elements)
    else:
        raise Exception('argument returning must be list, dictionary or tuple.')
