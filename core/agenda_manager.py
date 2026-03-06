from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass
class Event:
    title: str
    start: datetime
    end: datetime
    description: str = ""
    priority: str = "Média"
    category: str = "Geral"
    color: str = "#00FFFF"
    recurring: bool = False
    id: int | None = None


class AgendaManager:
    def __init__(self):
        self.events: list[Event] = []
        self._next_id = 1

    def add_event(self, event: Event) -> Event:
        if event.end <= event.start:
            raise ValueError("Horário final deve ser maior que o inicial.")
        if event.id is None:
            event.id = self._next_id
            self._next_id += 1
        self.events.append(event)
        self.events.sort(key=lambda item: item.start)
        return event

    def remove_event(self, event_id: int) -> None:
        self.events = [event for event in self.events if event.id != event_id]

    def get_events_day(self, day: date) -> list[Event]:
        day_start = datetime.combine(day, time.min)
        day_end = datetime.combine(day, time.max)
        return [
            event
            for event in self.events
            if event.start <= day_end and event.end >= day_start
        ]

    def get_events_for_day(self, day: date) -> list[Event]:
        return self.get_events_day(day)

    def get_events_for_week(self, day: date) -> list[Event]:
        days = self.week_days(day)
        week_start = datetime.combine(days[0], time.min)
        week_end = datetime.combine(days[-1], time.max)
        return [
            event
            for event in self.events
            if event.start <= week_end and event.end >= week_start
        ]

    def get_events_month(self, year: int, month: int) -> list[Event]:
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(microseconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(microseconds=1)
        return [
            event
            for event in self.events
            if event.start <= month_end and event.end >= month_start
        ]

    def week_days(self, day: date) -> list[date]:
        monday = day - timedelta(days=day.weekday())
        return [monday + timedelta(days=offset) for offset in range(7)]

    def build_datetime(self, day: date, hhmm: str) -> datetime:
        hour, minute = hhmm.strip().split(":")
        return datetime(
            day.year,
            day.month,
            day.day,
            int(hour),
            int(minute),
        )
