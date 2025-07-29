# Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International

# © 2025 Sam Afzali

# This work is licensed under the Creative Commons Attribution‑NonCommercial‑NoDerivatives 4.0 International License.

# You are free to:
#   ✔️ Share — copy and redistribute the material in any medium or format  
#     • **Attribution** is required: You must give appropriate credit to Sam Afzali, provide a link to the license, and indicate if changes were made.  
#     • **NonCommercial**: You may not use the material for commercial purposes.  
#     • **NoDerivatives**: If you remix, transform, or build upon the material, you may not distribute the modified material.

# Under the following terms:
#  1. **Attribution** — You must credit “Smart Time” and its author **Sam Afzali** in any use or redistribution.  
#  2. **NonCommercial** — You may not sell, license, or use this library for commercial gain.  
#  3. **NoDerivatives** — You may not alter, transform, or build upon this work.

# No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

# Author Contact: Sam Afzali | GitHub: https://github.com/samafzali11

# **Smart Time™** is a trademark of Sam Afzali. All rights reserved.

import re
from datetime import datetime, timedelta, timezone
try:
    import pytz
except ImportError:
    pytz = None
try:
    import pandas as pd
except ImportError:
    pd = None

class SmartTime:
    #Time units (in seconds)
    _units = {
        'nanosecond': 1e-9, 'ns': 1e-9,
        'microsecond': 1e-6, 'µs': 1e-6, 'us': 1e-6,
        'millisecond': 1e-3, 'ms': 1e-3,
        'second': 1, 's': 1, 'sec': 1, 'ث': 1, 'ثانیه': 1,
        'minute': 60, 'm': 60, 'min': 60, 'د': 60, 'دقیقه': 60,
        'hour': 3600, 'h': 3600, 'hr': 3600, 'س': 3600, 'ساعت': 3600,
        'day': 86400, 'd': 86400, 'روز': 86400,
        'week': 604800, 'w': 604800, 'ه': 604800, 'هفته': 604800,
        'month': 2629800, 'mo': 2629800, 'ماه': 2629800,
        'year': 31557600, 'y': 31557600, 'سال': 31557600,
    }
    _normalize = {
        **{k: 'second' for k in ('s','sec','ث','ثانیه')},
        **{k: 'minute' for k in ('m','min','د','دقیقه')},
        **{k: 'hour' for k in ('h','hr','س','ساعت')},
        **{k: 'day' for k in ('d','روز')},
        **{k: 'week' for k in ('w','ه','هفته')},
        **{k: 'month' for k in ('mo','ماه')},
        **{k: 'year' for k in ('y','سال')},
        'ms':'millisecond','nanosecond':'nanosecond','microsecond':'microsecond',
        'µs':'microsecond','us':'microsecond','ns':'nanosecond'
    }
    _ordered = [
        'year','month','week','day','hour','minute',
        'second','millisecond','microsecond','nanosecond'
    ]
    _re = re.compile(r'(\d+\.?\d*)\s*([a-zA-Z\u0600-\u06FFµ]+)')

    def _parse_value_unit(self, text: str) -> float:
        total = 0.0
        for val, unit in self._re.findall(text):
            u = unit.lower()
            if u in self._units:
                total += float(val) * self._units[u]
        return total

    def parse(self, text: str) -> float:
        #Convert natural text to seconds (float)
        return self._parse_value_unit(text)

    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        #Convert a number between two specified units
        fu, tu = from_unit.lower(), to_unit.lower()
        if fu not in self._units or tu not in self._units:
            raise ValueError(f"Unit '{from_unit}' Or '{to_unit}' Not Supported")
        sec = value * self._units[fu]
        return sec / self._units[tu]

    def total(self, items: list, to: str='second') -> float:
        #Sum multiple text values ​​and convert to a single unit
        total_sec = sum(self.parse(it) for it in items)
        return self.convert(total_sec, 'second', to)

    def explain(self, text: str) -> dict:
        #A parsed representation of each unit of text
        breakdown = {}
        for val, unit in self._re.findall(text):
            u = unit.lower()
            norm = self._normalize.get(u)
            if norm:
                breakdown.setdefault(norm, 0.0)
                breakdown[norm] += float(val)
        return breakdown

    def format(self, seconds: float, lang: str='en') -> str:
        #Detailed format: '1 day 3 hours 4 minutes' or Persian equivalent
        rem = seconds
        parts = []
        labels = {
            'en': {
                'year':'year','month':'month','week':'week','day':'day',
                'hour':'hour','minute':'minute','second':'second',
                'millisecond':'ms','microsecond':'µs','nanosecond':'ns'
            },
            'fa': {
                'year':'سال','month':'ماه','week':'هفته','day':'روز',
                'hour':'ساعت','minute':'دقیقه','second':'ثانیه',
                'millisecond':'میلی‌ثانیه','microsecond':'میکروثانیه','nanosecond':'نانوثانیه'
            }
        }[lang]
        for unit in self._ordered:
            sec = self._units[unit]
            if rem >= sec:
                amt = int(rem // sec)
                rem -= amt * sec
                parts.append(f"{amt} {labels[unit]}")
        return ' '.join(parts) or f"0 {labels['second']}"

    def to_iso8601(self, seconds: float) -> str:
        #Constructing an ISO 8601 duration string
        rem = seconds
        date_p, time_p = [], []
        codes = {'year':'Y','month':'M','week':'W','day':'D',
                 'hour':'H','minute':'M','second':'S'}
        for unit in ('year','month','week','day'):
            sec = self._units[unit]
            if rem >= sec:
                amt = int(rem // sec); rem -= amt*sec
                date_p.append(f"{amt}{codes[unit]}")
        for unit in ('hour','minute','second'):
            sec = self._units[unit]
            if rem >= sec:
                amt = int(rem // sec); rem -= amt*sec
                time_p.append(f"{amt}{codes[unit]}")
        iso = "P" + ''.join(date_p)
        if time_p: iso += "T" + ''.join(time_p)
        return iso or "P0D"

    def parse_iso8601(self, text: str) -> float:
        #Read ISO 8601 duration → seconds
        #Separate the date/time part
        date_str, time_str = text.strip().lstrip('P').split('T') if 'T' in text else (text.lstrip('P'),'')
        total = 0.0
        mapping = {'Y':31557600,'M':2629800,'W':604800,'D':86400,'H':3600,'M_time':60,'S':1}
        #Date
        for num, code in re.findall(r'(\d+)([YMWD])', date_str):
            total += float(num) * mapping[code]
        #Time
        for num, code in re.findall(r'(\d+)([HMS])', time_str):
            key = code if code!='M' else 'M_time'
            total += float(num) * mapping[key]
        return total

    def now(self, tz: str=None) -> 'DateTimeHelper':
        #Current time (UTC or with timezone)
        dt = datetime.now(timezone.utc)
        if tz and pytz:
            dt = dt.astimezone(pytz.timezone(tz))
        return DateTimeHelper(dt)

    def supported_units(self) -> list:
        return sorted(set(self._normalize.values()))

class Duration:
    #Time frame with additional features
    def __init__(self, seconds: float):
        self.seconds = seconds

    @classmethod
    def from_text(cls, text: str):
        return cls(SmartTime().parse(text))

    @classmethod
    def from_iso(cls, iso: str):
        return cls(SmartTime().parse_iso8601(iso))

    def to(self, unit: str) -> float:
        return SmartTime().convert(self.seconds, 'second', unit)

    def to_timedelta(self) -> timedelta:
        return timedelta(seconds=self.seconds)

    def to_pandas(self):
        if pd:
            return pd.to_timedelta(self.seconds, unit='s')
        raise ImportError("For pandas, you need to install pandas")

    def __add__(self, other):
        if isinstance(other, Duration):
            return Duration(self.seconds + other.seconds)
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, Duration):
            return Duration(self.seconds - other.seconds)
        raise TypeError

    def __str__(self):
        return SmartTime().format(self.seconds)

    def to_iso(self):
        return SmartTime().to_iso8601(self.seconds)

class DateTimeHelper:
    #Working with datetime and Duration
    def __init__(self, dt: datetime):
        self.dt = dt

    def add(self, duration: Duration) -> datetime:
        return self.dt + duration.to_timedelta()

    def subtract(self, duration: Duration) -> datetime:
        return self.dt - duration.to_timedelta()

    @staticmethod
    def diff(dt1: datetime, dt2: datetime) -> Duration:
        delta = dt1 - dt2
        return Duration(delta.total_seconds())

    @staticmethod
    def business_days(dt1: datetime, dt2: datetime) -> int:
        days = abs((dt1.date() - dt2.date()).days)
        weeks, rem = divmod(days, 7)
        return weeks*5 + sum(1 for i in range(rem) if (dt2.weekday()+i)%7 < 5)

class Timer:
    #ContextManager for measuring execution time
    def __enter__(self):
        self._start = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type, exc, tb):
        self._end = datetime.now(timezone.utc)
        self.elapsed = (self._end - self._start).total_seconds()
