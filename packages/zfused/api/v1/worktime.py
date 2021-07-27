# coding:utf-8
# --author-- lanhua.zhou

import time
import datetime
import logging


class WorkHours(object):
    def __init__(self, start_date, end_date, worktiming = ["09:30", "18:00"], weekends = [6, 7]):
        self._weekends = weekends
        self._worktiming = worktiming
        self._start_date = start_date
        self._end_date = end_date
        self._day_hours = (int(self._worktiming[1].split(":")[0]) - int(self._worktiming[0].split(":")[0])) + (int(self._worktiming[1].split(":")[1]) - int(self._worktiming[0].split(":")[1]))/60.0
        self._day_minutes = self._day_hours * 60 

        self._days_off = weekends
        self._days_work = [x for x in range(7) if x not in self._days_off]

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, date):
        self._start_date = date

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, date):
        self._end_date = date

    def getdays(self):
        """ get days

        """
        return int(self.getminutes() / self._day_minutes)
    
    def gethours(self):
        """ get hours
        """
        return '%.1f' % (self.getminutes()/60 + (self.getminutes() % 60)/60.0)

    def getminutes(self):
        """ Return the difference in minutes.
        """
        # Set initial default variables
        dt_start = self.start_date  # datetime of start
        dt_end = self.end_date    # datetime of end
        worktime_in_seconds = 0

        if dt_start.date() == dt_end.date():
            # starts and ends on same workday
            full_days = 0
            if self.is_weekend(dt_start):
                return 0
            else:
                if "%02d:%02d"%(dt_start.hour, dt_start.minute) < self._worktiming[0]:
                    # set start time to opening hour
                    dt_start = datetime.datetime(
                        year=dt_start.year,
                        month=dt_start.month,
                        day=dt_start.day,
                        hour = int(self._worktiming[0].split(":")[0]),
                        minute = int(self._worktiming[0].split(":")[1]))
                if "%02d:%02d"%(dt_start.hour, dt_start.minute) >= self._worktiming[1] or "%02d:%02d"%(dt_end.hour, dt_end.minute) < self._worktiming[0]:
                    return 0    
                if "%02d:%02d"%(dt_end.hour, dt_end.minute) >= self._worktiming[1]:
                    dt_end = datetime.datetime(
                        year=dt_end.year,
                        month=dt_end.month,
                        day=dt_end.day,
                        hour= int(self._worktiming[1].split(":")[0]),
                        minute= int(self._worktiming[1].split(":")[1]) )
                worktime_in_seconds = (dt_end-dt_start).total_seconds()
        elif (dt_end-dt_start).days < 0:
            # ends before start
            return 0
        else:
            # start and ends on different days
            current_day = dt_start  # marker for counting workdays
            while not current_day.date() == dt_end.date():
                if not self.is_weekend(current_day):
                    if current_day == dt_start:
                        # increment hours of first day
                        if "%02d:%02d"%(current_day.hour, current_day.minute) < self._worktiming[0]:
                            # starts before the work day
                            worktime_in_seconds += self._day_minutes*60  # add 1 full work day
                        elif "%02d:%02d"%(current_day.hour, current_day.minute)  >= self._worktiming[1]:
                            pass  # no time on first day
                        else:
                            # starts during the working day
                            dt_currentday_close = datetime.datetime(
                                year=dt_start.year,
                                month=dt_start.month,
                                day=dt_start.day,
                                hour = int(self._worktiming[1].split(":")[0]),
                                minute = int(self._worktiming[1].split(":")[1]))
                            worktime_in_seconds += (dt_currentday_close
                                         - dt_start).total_seconds()
                    else:
                        # increment one full day
                        worktime_in_seconds += self._day_minutes*60
                current_day += datetime.timedelta(days=1)  # next day
            # Time on the last day
            if not self.is_weekend(dt_end):
                if "%02d:%02d"%(dt_end.hour, dt_end.minute) >= self._worktiming[1]:  # finish after close
                    # Add a full day
                    worktime_in_seconds += self._day_minutes*60
                elif "%02d:%02d"%(dt_end.hour, dt_end.minute) < self._worktiming[0]:  # close before opening
                    pass  # no time added
                else:
                    # Add time since opening
                    dt_end_open = datetime.datetime(
                        year=dt_end.year,
                        month=dt_end.month,
                        day=dt_end.day,
                        hour = int(self._worktiming[0].split(":")[0]),
                        minute = int(self._worktiming[0].split(":")[1]))
                    worktime_in_seconds += (dt_end-dt_end_open).total_seconds()
        return int(worktime_in_seconds / 60)

    def is_weekend(self, datetime):
        """ Returns True if datetime lands on a weekend.
        
        """
        for weekend in self._weekends:
            if datetime.isoweekday() == weekend:
                return True
        return False

    def days(self):
        return (self.end_date - self.start_date).days

    def work_days(self):
        """ 实现工作日的 iter, 从start_date 到 end_date , 如果在工作日内,yield 日期
        """
        # 还没排除法定节假日
        tag_date = self.start_date
        while True:
            if tag_date > self.end_date:
                break
            if tag_date.weekday() in self._days_work:
                yield tag_date
            tag_date += datetime.timedelta(days=1)