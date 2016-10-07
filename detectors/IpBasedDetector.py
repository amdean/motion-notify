__author__ = 'adean'

import subprocess
import ConfigParser
import logging

logger = logging.getLogger('MotionNotify')

class IpBasedDetector:
    @staticmethod
    def detect_presence(config):
        logger.debug("IpBasedDetector detecting presence")
        ip_addresses = None
        ping_timeout_seconds = 2
        ping_timeout_switch = "-w"
        try:
            ip_addresses = config.config_obj.get('IpBasedDetector', 'ip_addresses')
            ping_timeout_seconds = config.config_obj.get('IpBasedDetector', 'ping_timeout_seconds')
            ping_timeout_switch = config.config_obj.get('IpBasedDetector', 'ping_timeout_switch')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass

        if not ip_addresses:
            logger.info("No IP addresses configured - skipping IP check")
            return True
        logger.info("Checking for presence via IP address")
        addresses = ip_addresses.split(',')
        for address in addresses:
            logger.debug("IpBasedDetector checking IP: " + address)
            test_string = 'bytes from'
            results = subprocess.Popen(['ping', '-c1', ping_timeout_switch + ping_timeout_seconds, address],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT).stdout.readlines()
            logger.info("Nmap result %s", results)
            for result in results:
                if test_string in result:
                    logger.info('IpBasedDetector: IP detected - someone is home')
                    return False
        logger.info('IpBasedDetector: IP inactive - nobody is home - system is active')
        return True
