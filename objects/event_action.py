__author__ = 'adean'

from enums import trigger_rule as trigger_rule_mod
class EventAction(object):
    def __init__(self, action_name, trigger_rule_str):
        self.action_name = action_name
        self.trigger_rule = trigger_rule_mod.TriggerRule[trigger_rule_str]
