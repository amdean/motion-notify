__author__ = 'adean'

from enums import trigger_rule
class EventAction(object):
    def __init__(self, action_name, trigger_rule_str):
        self.action_name = action_name
        self.trigger_rule = trigger_rule.TriggerRule[trigger_rule_str]
