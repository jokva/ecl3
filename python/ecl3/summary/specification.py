from __future__ import division
from .. import core

import datetime
import logging
import itertools

def timestamp(xs):
    return datetime.datetime(
        year    = xs[0],
        month   = xs[1],
        day     = xs[2],
        hour    = xs[3],
        minute  = xs[4],
        second  = xs[5],
    )

class runtime_monitor(object):
    def __init__(self):
        self.finished = None
        self.initial_reportno = None
        self.current_reportno = None
        self.initial_timestamp = None
        self.current_timestamp = None
        self.basic = None
        self.double = None

class Summary(object):

    def __init__(self, keywords = None):
        """
        __init__ sets all its members to None by default, to be able to
        distinguish un-set values from set-but-empty

        If keywords is not None, it sets as many of the internal variables as
        it can.

        Parameters
        ----------
        keywords : iterable of (str, array_like)
            keywords, as derived from an SMSPEC file
        """

        # mandatory
        # according to the manual, these fields are mandatory to make sense of
        # the summary
        self.nlist = None
        self.gridshape = None
        self.istar = None
        self.keywords = None
        self.wgnames = None
        self.nums = None
        self.measurements = None
        self.units = None
        self.startdate = None

        # optional
        # these fields are optional, but the lgr-related fields are requried if
        # local grid refinement is used.
        self.restart = None
        self.unitsystem = None
        self.simulator = None
        self.names = None
        self.lgrs = None
        self.numlx = None
        self.numly = None
        self.numlz = None
        self.lengths = None
        self.lenunits = None
        self.lgrnames = None
        self.lgrvec = None
        self.lgrtimes = None
        self.runtime_monitor = None
        self.step_reason = None
        self.xcoord = None
        self.ycoord = None
        self.timestamp = None

        # a store of seen keywords, to preserve non-standard keys should they
        # be passed
        self.index = {}

        # accept both dict and key-value pairs
        try:
            items = keywords.items()
            # if this is a dict, make sure DIMENS is handled first
            # because other values depend on DIMENS already being read
            # for already-order collections this is a caller responsibility
            if 'DIMENS' in keywords:
                head = ('DIMENS', keywords['DIMENS'])
                items = itertools.chain([head], items)
        except AttributeError:
            items = keywords

        for key, value in items:
            self.update(key, value)

    def update(self, key, values):
        """

        Update and set the attributes from a keyword

        Parameters
        ----------
        key : str
            Summary specification keyword name to set
        values : array_like
            Summary specification keyword values to set

        Notes
        -----
        If an keyword not in the above list is given to this function, it is
        recorded in the index, and an info message is added to the log.
        Otherwise, this is considered a no-op.

        Supported keywords:
            INTEHEAD
            RESTART
            DIMENS
            KEYWORDS
            WGNAMES
            NAMES
            NUMS
            LGRS
            NUMLX
            NUMLY
            NUMLZ
            LENGTHS
            LENUNITS
            MEASRMNT
            UNITS
            STARTDAT
            LGRNAMES
            LGRVEC
            LGRTIMES
            RUNTIMEI
            RUNTIMED
            STEPRESN
            XCOORD
            YCOORD
            TIMESTMP
        """
        key = key.strip()

        if key == 'INTEHEAD':
            us = core.unitsystem(values[0])
            sim = core.simulatorid(values[1])

            # Don't crash unless warning-as-errors are on on broken simulator ID or
            # unit system.  If these values are wrong then it's very likely that the
            # entire file is unreliable, but that's call is the caller's
            if us is not None:
                self.unitsystem = us
            else:
                source = 'INTEHEAD[0] was {}'.format(values[0])
                problem = 'got INTEHEAD, but with invalid unit system'
                effect = 'unitsystem not updated'
                logging.info(source)
                logging.warning(' - '.join((problem, effect)))

            if sim is not None:
                self.simulator = sim
            else:
                source = 'INTEHEAD[1] was {}'.format(values[1])
                problem = 'got INTEHEAD, but with invalid simulator ID'
                effect = 'simulator not updated'
                logging.info(source)
                logging.warning(' - '.join((problem, effect)))

        elif key == 'DIMENS':
            nlist = values[0]
            gridshape = (values[1], values[2], values[3])
            istar = (values[5])
            self.nlist = nlist
            self.gridshape = gridshape
            self.istar = istar

        elif key == 'MEASRMNT':
            def grouper(iterable, n):
                # grouper('ABCDEFGHI', 3) --> ABC DEF GHI
                args = [iter(iterable)] * n
                return itertools.zip_longest(*args)

            if len(values) % self.nlist != 0:
                raise ValueError('measurement blocks does not evenly divide NLIST')

            blocks = len(values) / self.nlist
            groups = grouper(values, int(blocks))
            self.measurements = [''.join(group).strip() for group in groups]

        elif key == 'RESTART':
            self.restart = ''.join(values).strip()

        elif key == 'KEYWORDS':
            self.keywords = [x.strip() for x in values]

        elif key == 'WGNAMES':
            self.wgnames = [x.strip() for x in values]

        elif key == 'NAMES':
            self.names = [x.strip() for x in values]

        elif key == 'NUMS':
            self.nums = list(values)

        elif key == 'LGRS':
            self.lgrs = [x.strip() for x in values]

        elif key == 'NUMLX':
            self.numlx = list(values)

        elif key == 'NUMLY':
            self.numly = list(values)

        elif key == 'NUMLZ':
            self.numlz = list(values)

        elif key == 'LENGTHS':
            self.lengths = list(values)

        elif key == 'LENUNITS':
            # TODO: assert len(values) == 1?
            self.lenunits = values[0]

        elif key == 'UNITS':
            self.units = [x.strip() for x in values]

        elif key == 'STARTDAT':
            mega = 1000000
            second = values[5] // mega
            microsecond = values[5] - (second * mega)
            self.startdate = datetime.datetime(
                day = values[0],
                month = values[1],
                year = values[2],
                hour = values[3],
                minute = values[4],
                second = second,
                microsecond = microsecond,
            )

        elif key == 'LGRNAMES':
            self.lgrnames = [x.strip() for x in values]

        elif key == 'LGRVEC':
            self.lgrvec = list(values)

        elif key == 'LGRTIMES':
            self.lgrtimes = list(values)

        elif key == 'RUNTIMEI':
            if self.runtime_monitor is None:
                self.runtime_monitor = runtime_monitor()

            finished = values[0]
            initial = values[1]
            current = values[2]
            initial_ts = timestamp(values[3:9])
            current_ts = timestamp(values[9:15])
            basic = values[34]

            monitor = self.runtime_monitor

            if finished in (1, 2):
                monitor.finished = finished == 2
            else:
                msg = 'invalid finished value in RUNTIMEI, was {}'
                logging.warning(msg.format(finished))

            monitor.initial_reportno = initial
            monitor.current_reportno = current
            monitor.initial_timestamp = initial_ts
            monitor.current_timestamp = current_ts
            monitor.basic = basic

        elif key == 'RUNTIMED':
            if self.runtime_monitor is None:
                self.runtime_monitor = runtime_monitor()
            self.runtime_monitor.double = list(values)

        elif key == 'STEPRESN':
            self.step_reason = ''.join(values).strip()

        elif key == 'XCOORD':
            self.xcoord = list(values)

        elif key == 'YCOORD':
            self.ycoord = list(values)

        elif key == 'TIMESTMP':
            self.timestamp = timestamp(values)

        else:
            msg = 'unhandled keyword {}, not updating'
            logging.info(msg.format(key))

        self.index[key] = values
        return self

    def check_integrity(self):
        """
        Verify that the minimum required data is set.

        Does not enforce the presence of the RESTART keyword, although the
        manual assumes it is there
        """
        self.len_consistent('keywords')
        self.len_consistent('wgnames')
        self.len_consistent('nums')
        self.len_consistent('measurements')
        self.len_consistent('units')

        self.len_consistent('names', none_ok = True)
        self.len_consistent('lgrs', none_ok = True)
        self.len_consistent('numlx', none_ok = True)
        self.len_consistent('numly', none_ok = True)
        self.len_consistent('numlz', none_ok = True)
        self.len_consistent('lengths', none_ok = True)
        self.len_consistent('xcoord', none_ok = True)
        self.len_consistent('ycoord', none_ok = True)

    def len_consistent(self, attr, none_ok = False):
        """ length of var consistent with nlist

        Most arrays in the summary format must be of length nlist. This
        function raises ValueError if this does not hold for self.attr

        Parameters
        ----------
        attr : str
            name of attribute to check against nlist

        Raises
        ------
        ValueError
            If len(self.attr) != self.nlist

        Notes
        -----
        This is meant for internal use.

        """
        var = getattr(self, attr)

        if var is None and none_ok:
            return

        problem = 'nlist or {} inconsistent: '
        symptom = 'len({}) (= {}) != nlist (= {})'
        if len(var) != self.nlist:
            p = problem.format(attr)
            s = symptom.format(attr, len(var), self.nlist)
            raise ValueError(p + s)

    @staticmethod
    def load(keywords):
        s = Summary(keywords)
        s.check_integrity()
        return s

def load(path):
    stream = core.stream(path)
    return Summary.load((k.keyword, k.values) for k in stream.keywords())
