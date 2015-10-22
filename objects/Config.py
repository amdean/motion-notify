__author__ = 'adean'

import ConfigParser
from objects import EventAction


class Config(object):
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)

        self.set_on_event_start_event_list(self.config.get('EventActionRules', 'on_event_start'))
        self.set_on_event_start_event_list(self.config.get('EventActionRules', 'on_event_start'))
        self.set_on_event_start_event_list(self.config.get('EventActionRules', 'on_event_start'))
        self.on_picture_save_event_list = self.getEventActions(self.config.get('EventActionRules', 'on_picture_save'))
        self.on_movie_end_event_list = self.getEventActions(self.config.get('EventActionRules', 'on_movie_end'))

    def set_on_event_start_event_list(self, config_entry):
        self.on_event_start_event_list = self.getEventActions(config_entry)

    def set_on_picture_save_event_list(self, config_entry):
        self.on_picture_save_event_list = self.getEventActions(self, config_entry)

    def set_on_movie_end_event_list(self, config_entry):
        self.on_movie_end_event_list = self.getEventActions(self, config_entry)

    def getEventActions(self, configEntry):
        eventActions = []
        for entry in configEntry.split(','):
            elements = entry.split(":")
            eventActions.append(EventAction.EventAction(elements[0], elements[1]))
        return eventActions
