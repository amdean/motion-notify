__author__ = 'adean'

from enums import TriggerRule
class EventAction(object):
    def __init__(self, action_name, trigger_rule):
        self.action_name = action_name
        self.trigger_rule = TriggerRule.TriggerRule[trigger_rule]
