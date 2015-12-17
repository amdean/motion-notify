__author__ = 'adean'

import os
from enums import event_type as event_type_mod
from enums import trigger_rule as trigger_rule_mod

class MotionEvent(object):
    def __init__(self, media_file, event_type, event_time, event_id, file_type):
        self.media_file = media_file
        self.event_time = event_time
        self.event_id = event_id
        self.file_type = file_type
        self.event_type = event_type
        self.upload_url = ""

    def get_event_actions_for_event(self, config):
        if self.event_type == event_type_mod.EventType.on_event_start:
            return config.on_event_start_event_action_list;
        elif self.event_type == event_type_mod.EventType.on_picture_save:
            return config.on_picture_save_event_action_list;
        elif self.event_type == event_type_mod.EventType.on_movie_end:
            return config.on_movie_end_event_action_list;

    def get_actions_for_event(self, config, is_system_active):
        list_of_event_actions = self.get_event_actions_for_event(config);
        actions_to_perform = []
        for event_action in list_of_event_actions:
            if event_action.trigger_rule == trigger_rule_mod.TriggerRule.always or (
                            event_action.trigger_rule == trigger_rule_mod.TriggerRule.if_active and is_system_active):
                actions_to_perform.append(event_action.action_name)
        return actions_to_perform

    def get_mime_type(self):
        if self.media_file.endswith(("jpg", "png", "gif", "bmp")):
            return "image/" + self.file_type
        else:
            return "video/" + self.file_type

    def get_upload_filename(self):
        return self.event_id.__str__() + "_" + self.event_time.__str__() + os.path.splitext(self.media_file)[
            1].__str__()
