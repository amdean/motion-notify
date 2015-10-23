__author__ = 'adean'

from enum import Enum


class TriggerRule(Enum):
    always = 1
    if_active = 2
