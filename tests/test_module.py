__author__ = 'adean'

import unittest
from objects import Config
from objects import MotionEvent
from objects.enums import EventType
from objects.enums import TriggerRule


class MotionNotifyTestSuite(unittest.TestCase):

    def setUp(self):
        self.config = Config.Config("../motion-notify.cfg")
        self.config.set_on_event_start_event_action_list("SmtpEmailNotifyAction:if_active")
        self.config.set_on_picture_save_event_action_list(
            "GoogleDriveUploadAction:always,SmtpEmailNotifyAction:if_active")
        self.config.set_on_movie_end_event_action_list("SmtpEmailNotifyAction:if_active")
        pass

    def test_get_event_action_from_config_entry(self):
        event_actions = self.config.on_event_start_event_action_list
        self.assertEqual(1, event_actions.__len__())
        self.assertEqual(event_actions[0].action_name, "SmtpEmailNotifyAction")
        self.assertEqual(event_actions[0].trigger_rule, TriggerRule.TriggerRule.if_active)

        event_actions = self.config.on_picture_save_event_action_list
        self.assertEqual(2, event_actions.__len__())
        self.assertEqual(event_actions[0].action_name, "GoogleDriveUploadAction")
        self.assertEqual(event_actions[0].trigger_rule, TriggerRule.TriggerRule.always)
        self.assertEqual(event_actions[1].action_name, "SmtpEmailNotifyAction")
        self.assertEqual(event_actions[1].trigger_rule, TriggerRule.TriggerRule.if_active)

    def test_motion_event_get_actions_for_event(self):
        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_event_start)
        event_actions = motion_event.get_event_actions_for_event(self.config)
        self.assertEqual(1, event_actions.__len__())

        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_picture_save)
        event_actions = motion_event.get_event_actions_for_event(self.config)
        self.assertEqual(2, event_actions.__len__())

    def test_get_actions_for_event(self):
        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_event_start)
        list_of_actions = motion_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_picture_save)
        list_of_actions = motion_event.get_actions_for_event(self.config, True)
        self.assertEqual(2, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_movie_end)
        list_of_actions = motion_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        # test that if the system is inactive "if_active" events are not triggered
        motion_event = MotionEvent.MotionEvent('', 1234567890, 11, 'jpg', EventType.EventType.on_picture_save)
        list_of_actions = motion_event.get_actions_for_event(self.config, False)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)


if __name__ == '__main__':
    unittest.main()
