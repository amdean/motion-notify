__author__ = 'adean'

from datetime import time
from datetime import datetime

import logging

logger = logging.getLogger('MotionNotify')

class TimeBasedDetector:
    @staticmethod
    def detect_presence(config):
        logger.debug("TimeBasedDetector: detecting presence")
        return TimeBasedDetector.check_time_ranges(TimeBasedDetector.get_time_ranges(
            config.config_obj.get('TimeBasedDetector', 'time_ranges')), datetime.now().time())

    @staticmethod
    def check_time_ranges(time_ranges, current_time):
        for time_range in time_ranges:
            if time_range.start_time <= current_time <= time_range.end_time:
                logger.info(
                    'TimeBasedDetector: System is active due to TimeBasedDetector: ' + time_range.start_time.strftime(
                    "%H:%M") + " - " + time_range.end_time.strftime("%H:%M"))
                return True
        logger.info('System is inactive based on TimeBasedDetector')
        return False

    @staticmethod
    def get_time_ranges(config_entry):
        logger.debug("TimeBasedDetector: getting time ranges for config entry: " + config_entry)
        time_ranges = []
        time_range_entries = config_entry.split(",")
        for time_range_entry in time_range_entries:
            time_rangetime_str = time_range_entry.split("-")
            time_ranges.append(TimeRange(time_rangetime_str[0], time_rangetime_str[1]))
        return time_ranges


class TimeRange:
    def __init__(self, start_time, end_time):
        self.start_time = time(int(start_time.split(":")[0]), int(start_time.split(":")[1]))
        self.end_time = time(int(end_time.split(":")[0]), int(end_time.split(":")[1]))
