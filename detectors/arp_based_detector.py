__author__ = 'adean'

import subprocess
import ConfigParser


class ArpBasedDetector:
    def detect_presence(logger, config):
        presenceMacs = []
        network = None

        try:
            presenceMacs = config.get('ArpBasedDetector', 'presence_macs').split(',')
            network = config.get('ArpBasedDetector', 'network')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        if not network or not presenceMacs:
            return None
        logger.info("Checking for presence via MAC address")
        result = subprocess.Popen(['sudo', 'arp-scan', network], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT).stdout.readlines()
        logger.info("result %s", result)
        for addr in result:
            for i in presenceMacs:
                if i.lower() in addr.lower():
                    logger.info('ARP entry found - someone is home')
                    return False
        logger.info('No ARP entry found - nobody is home - system is active')
        return True
