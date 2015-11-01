__author__ = 'adean'

import ConfigParser
from objects import event_action as event_action_mod
from objects import detector_rules as detector_rules_mod


class Config(object):
    def __init__(self, config_file):
        self.config_obj = ConfigParser.ConfigParser()
        self.config_obj.read(config_file)

        self.on_event_start_event_action_list = []
        self.on_picture_save_event_action_list = []
        self.on_movie_end_event_action_list = []

        self.set_on_event_start_event_action_list(self.config_obj.get('EventActionRules', 'on_event_start'))
        self.set_on_picture_save_event_action_list(self.config_obj.get('EventActionRules', 'on_picture_save'))
        self.set_on_movie_end_event_action_list(self.config_obj.get('EventActionRules', 'on_movie_end'))

        self.detector_rule_set = detector_rules_mod.DetectorRuleSet(self.config_obj.get('Detection', 'detector_rules'))

    def set_on_event_start_event_action_list(self, config_entry):
        self.on_event_start_event_action_list = self.get_event_actions(config_entry)

    def set_on_picture_save_event_action_list(self, config_entry):
        self.on_picture_save_event_action_list = self.get_event_actions(config_entry)

    def set_on_movie_end_event_action_list(self, config_entry):
        self.on_movie_end_event_action_list = self.get_event_actions(config_entry)

    def get_event_actions(self, config_entry):
        event_actions = []
        for entry in config_entry.split(','):
            elements = entry.split(":")
            event_actions.append(event_action_mod.EventAction(elements[0], elements[1]))
        return event_actions
