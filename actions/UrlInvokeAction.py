"""UrlInvokeAction

An HTTP request is made to the URL's defined in the config file when the event start and event end actions occur.
No action is carried out when the do_action method is called
"""
__author__ = 'adean'

import logging
import requests

logger = logging.getLogger('MotionNotify')

class UrlInvokeAction:
    @staticmethod
    def do_event_start_action(config, motion_event_obj):
        UrlInvokeAction.make_request(config, motion_event_obj, 'event_start_url')

    @staticmethod
    def do_event_end_action(config, motion_event_obj):
        UrlInvokeAction.make_request(config, motion_event_obj, 'movie_end_url')

    @staticmethod
    def do_action(config, motion_event_obj):
        logger.debug("Motionevent_id:" + motion_event_obj.event_id + " UrlInvokeAction: Ignoring action")


    @staticmethod
    def make_request(config, motion_event_obj, config_entry):
        logger.debug("Motionevent_id:" + motion_event_obj.event_id + " UrlInvokeAction: Making request")
        url = config.config_obj.get('UrlInvokeAction', config_entry)
        logger.debug("Motionevent_id:" + motion_event_obj.event_id + " UrlInvokeAction: URL: " + url)
        r = requests.get(url)
        if r.status_code != requests.codes.ok:
            logger.error("Motionevent_id:" + motion_event_obj.event_id + " UrlInvokeAction: Request failed..." + r.reason)
        else:
            logger.info("Motionevent_id:" + motion_event_obj.event_id + " UrlInvokeAction: Request sent successfully")
