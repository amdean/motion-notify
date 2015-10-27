__author__ = 'adean'

from enums import EventType
from enums import TriggerRule

class MotionEvent(object):
    def __init__(self, mediaFile, event_type, eventTime, eventId, fileType):
        self.mediaFile = mediaFile
        self.eventTime = eventTime
        self.eventId = eventId
        self.fileType = fileType
        self.event_type = event_type

    def get_event_actions_for_event(self, config):
        if self.event_type == EventType.EventType.on_event_start:
            return config.on_event_start_event_action_list;
        elif self.event_type == EventType.EventType.on_picture_save:
            return config.on_picture_save_event_action_list;
        elif self.event_type == EventType.EventType.on_movie_end:
            return config.on_movie_end_event_action_list;

    def get_actions_for_event(self, config, is_system_active):
        list_of_event_actions = self.get_event_actions_for_event(config);
        actions_to_perform = []
        for event_action in list_of_event_actions:
            if event_action.trigger_rule == TriggerRule.TriggerRule.always or (
                    event_action.trigger_rule == TriggerRule.TriggerRule.if_active and is_system_active):
                actions_to_perform.append(event_action.action_name)
        return actions_to_perform
