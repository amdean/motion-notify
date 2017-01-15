__author__ = 'adean'

from enum import Enum


class EventType(Enum):
    on_event_start = 1
    on_picture_save = 2
    on_movie_end = 3
    on_cron_trigger = 4
