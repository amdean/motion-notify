__author__ = 'adean'

import subprocess
import ConfigParser


class IpBasedDetector:
    @staticmethod
    def detect_presence(logger, config):
        ip_addresses = None
        try:
            ip_addresses = config.config.get('IpBasedDetector', 'ip_addresses')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass

        if not ip_addresses:
            logger.info("No IP addresses configured - skipping IP check")
            return True
        logger.info("Checking for presence via IP address")
        addresses = ip_addresses.split(',')
        for address in addresses:
            test_string = 'bytes from'
            results = subprocess.Popen(['ping', '-c1', address], stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT).stdout.readlines()
            logger.info("Nmap result %s", results)
            for result in results:
                if test_string in result:
                    logger.info('IP detected - someone is home')
                    return False
        logger.info('IP inactive - nobody is home - system is active')
        return True
