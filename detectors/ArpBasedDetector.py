__author__ = 'adean'

import subprocess
import ConfigParser
import logging

logger = logging.getLogger('MotionNotify')

class ArpBasedDetector:
    @staticmethod
    def detect_presence(config):
        logger.debug("ArpBasedDetector: detecting presence")
        presence_macs = []
        network = None

        try:
            presence_macs = config.config_obj.get('ArpBasedDetector', 'presence_macs').split(',')
            network = config.get('ArpBasedDetector', 'network')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        if not network or not presence_macs:
            return None
        logger.info("ArpBasedDetector: Checking for presence via MAC address")
        result = subprocess.Popen(['sudo', 'arp-scan', network], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT).stdout.readlines()
        logger.info("result %s", result)
        for addr in result:
            for i in presence_macs:
                if i.lower() in addr.lower():
                    logger.info('ArpBasedDetector: ARP entry found - someone is home')
                    return False
        logger.info('ArpBasedDetector: No ARP entry found - nobody is home - system is active')
        return True
