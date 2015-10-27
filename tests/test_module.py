import sys

__author__ = 'adean'

import unittest
import logging.handlers
from datetime import time
from objects import config
from objects import motion_event
from objects.enums import EventType
from objects.enums import TriggerRule
from utils import utils
from actions import GoogleDriveUploadAction
from detectors import TimeBasedDetector
from objects.detector_rules import DetectorRuleSet


class MotionNotifyTestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger('MotionNotify')
        self.logger.level = logging.DEBUG
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.config = config.Config("../motion-notify.cfg")
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

    def test_motion_test_event_get_actions_for_event(self):
        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_event_start, 1234567890, 11, 'jpg')
        event_actions = motion_test_event.get_event_actions_for_event(self.config)
        self.assertEqual(1, event_actions.__len__())

        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_picture_save, 1234567890, 11, 'jpg')
        event_actions = motion_test_event.get_event_actions_for_event(self.config)
        self.assertEqual(2, event_actions.__len__())

    def test_get_actions_for_event(self):
        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_event_start, 1234567890, 11, 'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_picture_save, 1234567890, 11, 'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(2, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_movie_end, 1234567890, 11, 'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        # test that if the system is inactive "if_active" events are not triggered
        motion_test_event = motion_event.MotionEvent('', EventType.EventType.on_picture_save, 1234567890, 11, 'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, False)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)

    def test_reflection(self):
        klass = utils.Utils.reflect_class_from_classname('actions', 'GoogleDriveUploadAction')
        self.assertIsInstance(klass, GoogleDriveUploadAction.GoogleDriveUploadAction)

    def test_time_based_detector_check_time_ranges(self):
        time_ranges = TimeBasedDetector.TimeBasedDetector.get_time_ranges("01:00-07:00,12:00-13:00")
        self.assertTrue(TimeBasedDetector.TimeBasedDetector.check_time_ranges(self.logger, time_ranges, time(05, 12)))
        self.assertTrue(TimeBasedDetector.TimeBasedDetector.check_time_ranges(self.logger, time_ranges, time(12, 12)))
        self.assertFalse(
            TimeBasedDetector.TimeBasedDetector.check_time_ranges(self.logger, time_ranges, time(18, 12)))

    def test_detector_rules_get_rule_groups(self):
        detector_rule_set = DetectorRuleSet("{TimeBasedDetector,IPBasedDetector}{ArpBasedDetector}")
        self.assertEqual(2, detector_rule_set.detector_rule_groups.__len__())
        self.assertEqual("TimeBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[0])
        self.assertEqual("IPBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[1])
        self.assertEqual("ArpBasedDetector", detector_rule_set.detector_rule_groups[1].detectors[0])
        detector_rule_set = DetectorRuleSet("{ArpBasedDetector}")
        self.assertEqual("ArpBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[0])

    def test_get_status_from_detector_group(self):
        result = self.config.detector_rule_set.get_status_for_detector_rule_set(self.config, self.logger)
        # IpBasedDetector is looking for 127.0.0.1 so this always shows that the system is inactive as someone is home
        self.assertFalse(result);


if __name__ == '__main__':
    unittest.main()
