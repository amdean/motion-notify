__author__ = 'adean'

import unittest
from objects import Config


class MotionNotifyTestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_event_action_from_config_entry(self):
        config = Config.Config("../motion-notify.cfg")
        config.set_on_event_start_event_list("GoogleDriveUploadAction:Always,SmtpEmailNotifyAction:IfActive")
        eventActions = config.on_event_start_event_list
        self.assertEqual(eventActions[0].actionName, "GoogleDriveUploadAction")
        self.assertEqual(eventActions[0].triggerRule, "Always")
        self.assertEqual(eventActions[1].actionName, "SmtpEmailNotifyAction")
        self.assertEqual(eventActions[1].triggerRule, "IfActive")


if __name__ == '__main__':
    unittest.main()
