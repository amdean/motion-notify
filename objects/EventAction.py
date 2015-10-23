__author__ = 'adean'

from enums import TriggerRule
class EventAction(object):
    def __init__(self, actionName, trigger_rule):
        self.action_name = actionName
        self.trigger_rule = TriggerRule.TriggerRule[trigger_rule]
