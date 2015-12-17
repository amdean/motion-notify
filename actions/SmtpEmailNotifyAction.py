__author__ = 'adean'

import smtplib
import logging
from datetime import datetime

logger = logging.getLogger('MotionNotify')

class SmtpEmailNotifyAction:
    @staticmethod
    def do_event_start_action(config, motion_event_obj):
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " SmtpEmailNotifyAction: Sending start event email")
        msg = config.config_obj.get('SmtpEmailNotifyAction', 'event_started_message')
        msg += '\n\n' + config.config_obj.get('SmtpEmailNotifyAction', 'image_and_video_folder_link')
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " SmtpEmailNotifyAction: Initial config success")
        SmtpEmailNotifyAction.send_email(config, motion_event_obj, msg)

    @staticmethod
    def do_event_end_action(config, motion_event_obj):
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " Sending event end email")
        msg = config.config_obj.get('SmtpEmailNotifyAction', 'movie_end_message')
        msg += '\n\n' + motion_event_obj.upload_url
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " SmtpEmailNotifyAction: Initial config success")
        SmtpEmailNotifyAction.send_email(config, motion_event_obj, msg)

    @staticmethod
    def do_action(config, motion_event_obj):
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " Sending email")
        SmtpEmailNotifyAction.send_email(config, motion_event_obj, "")

    @staticmethod
    def send_email(config, motion_event_obj, msg):
        # SMTP account credentials
        username = config.config_obj.get('SmtpEmailNotifyAction', 'user')
        password = config.config_obj.get('SmtpEmailNotifyAction', 'password')
        from_name = config.config_obj.get('SmtpEmailNotifyAction', 'name')
        sender = config.config_obj.get('SmtpEmailNotifyAction', 'sender')

        # Recipient email address (could be same as from_addr)
        recipient = config.config_obj.get('SmtpEmailNotifyAction', 'recipient')

        # Subject line for email
        subject = config.config_obj.get('SmtpEmailNotifyAction', 'subject')

        logger.info("Motionevent_id:" + motion_event_obj.event_id + " SmtpEmailNotifyAction: Full config success")

        senddate = datetime.strftime(datetime.now(), '%Y-%m-%d')
        m = "Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (
        senddate, from_name, sender, recipient, subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(sender, recipient, m + msg)
        server.quit()
        logger.info("Motionevent_id:" + motion_event_obj.event_id + " Email sent")
