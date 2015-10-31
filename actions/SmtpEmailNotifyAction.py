__author__ = 'adean'

import smtplib
from datetime import datetime

logger = logging.getLogger('MotionNotify')

class SmtpEmailNotifyAction:
    @staticmethod
    def do_event_start_action(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId + " Sending start event email")
        msg = config.get('SmtpEmailNotifier', 'event_started_message')
        msg += '\n\n' + config.get('SmtpEmailNotifier', 'image_and_video_folder_link')
        SmtpEmailNotifyAction.send_email(config, motion_event, msg)

    @staticmethod
    def do_event_end_action(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId + " Sending event end email")
        msg = config.get('SmtpEmailNotifier', 'message')
        msg += '\n\n' + motion_event.uploadUrl
        SmtpEmailNotifyAction.send_email(config, motion_event, msg)

    @staticmethod
    def do_action(config, motion_event):
        logger.info("MotionEventId:" + motion_event.eventId + " Sending email")
        SmtpEmailNotifyAction.send_email(config, motion_event, "")

    @staticmethod
    def send_email(config, motion_event, msg):
        # SMTP account credentials
        username = config.get('SmtpEmailNotifier', 'user')
        password = config.get('SmtpEmailNotifier', 'password')
        from_name = config.get('SmtpEmailNotifier', 'name')
        sender = config.get('SmtpEmailNotifier', 'sender')

        # Recipient email address (could be same as from_addr)
        recipient = config.get('SmtpEmailNotifier', 'recipient')

        # Subject line for email
        subject = config.get('SmtpEmailNotifier', 'subject')

        senddate = datetime.strftime(datetime.now(), '%Y-%m-%d')
        m = "Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (
        senddate, from_name, sender, recipient, subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(sender, recipient, m + msg)
        server.quit()
        logger.info("MotionEventId:" + motion_event.eventId + " Email sent")
