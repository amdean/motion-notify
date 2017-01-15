import os
import random
import sys
from uuid import UUID
import uuid


from actions.DeleteMediaFileAction import DeleteMediaFileAction

__author__ = 'adean'

import unittest
import logging.handlers
from datetime import time
from objects import config as config_mod
from objects import motion_event as motion_event_mod
from objects.enums import event_type as event_type_mod
from objects.enums import trigger_rule as trigger_rule_mod
from utils import utils as utils_mod
from actions import GoogleDriveUploadAction as google_drive_upload_action_mod
from actions import GoogleDriveCleanupAction as google_drive_cleanup_action_mod
from detectors import TimeBasedDetector as time_based_detector_mod
from objects.detector_rules import DetectorRuleSet as detector_rule_set_mod


class MotionNotifyTestSuite(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger('MotionNotify')
        if not self.logger.handlers:
            self.logger.level = logging.DEBUG
            self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self.config = config_mod.Config("../motion-notify-test.cfg")
        self.config.set_on_event_start_event_action_list("SmtpEmailNotifyAction:if_active")
        self.config.set_on_picture_save_event_action_list(
            "GoogleDriveUploadAction:always,SmtpEmailNotifyAction:if_active")
        self.config.set_on_movie_end_event_action_list("SmtpEmailNotifyAction:if_active")
        self.config.set_on_cron_trigger_action_list("GoogleDriveCleanupAction:always")
        pass

    def test_get_event_action_from_config_entry(self):
        event_actions = self.config.on_event_start_event_action_list
        self.assertEqual(1, event_actions.__len__())
        self.assertEqual(event_actions[0].action_name, "SmtpEmailNotifyAction")
        self.assertEqual(event_actions[0].trigger_rule, trigger_rule_mod.TriggerRule.if_active)

        event_actions = self.config.on_picture_save_event_action_list
        self.assertEqual(2, event_actions.__len__())
        self.assertEqual(event_actions[0].action_name, "GoogleDriveUploadAction")
        self.assertEqual(event_actions[0].trigger_rule, trigger_rule_mod.TriggerRule.always)
        self.assertEqual(event_actions[1].action_name, "SmtpEmailNotifyAction")
        self.assertEqual(event_actions[1].trigger_rule, trigger_rule_mod.TriggerRule.if_active)

        event_actions = self.config.on_cron_trigger_action_list
        self.assertEqual(1, event_actions.__len__())
        self.assertEqual(event_actions[0].action_name, "GoogleDriveCleanupAction")
        self.assertEqual(event_actions[0].trigger_rule, trigger_rule_mod.TriggerRule.always)

    def test_motion_test_event_get_actions_for_event(self):
        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_event_start, 1234567890, 11,
                                                         'jpg')
        event_actions = motion_test_event.get_event_actions_for_event(self.config)
        self.assertEqual(1, event_actions.__len__())

        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_picture_save, 1234567890, 11,
                                                         'jpg')
        event_actions = motion_test_event.get_event_actions_for_event(self.config)
        self.assertEqual(2, event_actions.__len__())

        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_cron_trigger, 1234567890, 11,
                                                         'jpg')
        event_actions = motion_test_event.get_event_actions_for_event(self.config)
        self.assertEqual(1, event_actions.__len__())

    def test_get_actions_for_event(self):
        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_event_start, 1234567890, 11,
                                                         'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_picture_save, 1234567890, 11,
                                                         'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(2, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_movie_end, 1234567890, 11,
                                                         'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, True)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("SmtpEmailNotifyAction", list_of_actions)

        # test that if the system is inactive "if_active" events are not triggered
        motion_test_event = motion_event_mod.MotionEvent('', event_type_mod.EventType.on_picture_save, 1234567890, 11,
                                                         'jpg')
        list_of_actions = motion_test_event.get_actions_for_event(self.config, False)
        self.assertEqual(1, list_of_actions.__len__())
        self.assertIn("GoogleDriveUploadAction", list_of_actions)

    def test_reflection(self):
        klass = utils_mod.Utils.reflect_class_from_classname('actions', 'GoogleDriveUploadAction')
        self.assertIsInstance(klass, google_drive_upload_action_mod.GoogleDriveUploadAction)

    def test_time_based_detector_check_time_ranges(self):
        time_ranges = time_based_detector_mod.TimeBasedDetector.get_time_ranges("01:00-07:00,12:00-13:00")
        self.assertTrue(time_based_detector_mod.TimeBasedDetector.check_time_ranges(time_ranges, time(05, 12)))
        self.assertTrue(time_based_detector_mod.TimeBasedDetector.check_time_ranges(time_ranges, time(12, 12)))
        self.assertFalse(
            time_based_detector_mod.TimeBasedDetector.check_time_ranges(time_ranges, time(18, 12)))

    def test_detector_rules_get_rule_groups(self):
        detector_rule_set = detector_rule_set_mod("{TimeBasedDetector,IPBasedDetector}{ArpBasedDetector}")
        self.assertEqual(2, detector_rule_set.detector_rule_groups.__len__())
        self.assertEqual("TimeBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[0])
        self.assertEqual("IPBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[1])
        self.assertEqual("ArpBasedDetector", detector_rule_set.detector_rule_groups[1].detectors[0])
        detector_rule_set = detector_rule_set_mod("{ArpBasedDetector}")
        self.assertEqual("ArpBasedDetector", detector_rule_set.detector_rule_groups[0].detectors[0])

    def test_get_status_from_detector_group(self):
        result = self.config.detector_rule_set.get_status_for_detector_rule_set(self.config)
        # IpBasedDetector is looking for 127.0.0.1 so this always shows that the system is inactive as someone is home
        self.assertFalse(result)

    def test_delete_media_file_action(self):
        motion_test_event = motion_event_mod.MotionEvent('/tmp/' + uuid.uuid1().__str__(),
                                                         event_type_mod.EventType.on_event_start, 1234567890, 11, 'jpg')

        text_file = open(motion_test_event.media_file, "w")
        text_file.write("output")
        text_file.close()
        self.assertTrue(os.path.isfile(motion_test_event.media_file))

        DeleteMediaFileAction.do_action(self.config, motion_test_event)
        self.assertFalse(os.path.isfile(motion_test_event.media_file))

    def test_motion_event_get_upload_filename(self):
        motion_test_event = motion_event_mod.MotionEvent('/tmp/' + uuid.uuid1().__str__() + '.jpg',
                                                         event_type_mod.EventType.on_event_start, 1234567890, 11, 'jpg')
        self.assertEqual(motion_test_event.get_upload_filename(),
                         motion_test_event.event_id.__str__() + "_" + motion_test_event.event_time.__str__() + ".jpg")

    def test_motion_event_get_mime(self):
        motion_test_event = motion_event_mod.MotionEvent('/tmp/' + uuid.uuid1().__str__() + '.jpg',
                                                         event_type_mod.EventType.on_event_start, 1234567890, 11, 'jpg')
        self.assertEqual(motion_test_event.get_mime_type(), "image/jpg")

    def test_upload_file(self):
        motion_test_event = motion_event_mod.MotionEvent('../resources/test.jpg',
                                                         event_type_mod.EventType.on_event_start, random.random(), 11, 'jpg')
        drive = google_drive_upload_action_mod.GoogleDriveUploadAction.setup_drive(self.config)
        folder = google_drive_upload_action_mod.GoogleDriveUploadAction.create_folder(drive, self.config)
        gfile = google_drive_upload_action_mod.GoogleDriveUploadAction.upload_file(drive, motion_test_event, folder)
        print gfile['title']
        list = drive.ListFile({'q': "title = '" + gfile['title'] + "' and '" + folder['id'] + "' in parents" }).GetList()
        self.assertEquals(list.__len__(), 1)



if __name__ == '__main__':
    unittest.main()
