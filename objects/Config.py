__author__ = 'adean'

import ConfigParser
from objects import EventAction


class Config(object):
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)

        self.on_event_start_event_action_list = []
        self.on_picture_save_event_action_list = []
        self.on_movie_end_event_action_list = []

        self.set_on_event_start_event_action_list(self.config.get('EventActionRules', 'on_event_start'))
        self.set_on_picture_save_event_action_list(self.config.get('EventActionRules', 'on_picture_save'))
        self.set_on_movie_end_event_action_list(self.config.get('EventActionRules', 'on_movie_end'))

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
            event_actions.append(EventAction.EventAction(elements[0], elements[1]))
        return event_actions
