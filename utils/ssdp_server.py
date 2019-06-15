#!/usr/bin/python2.7

""" Computer Vision Camera for SmartThings

Copyright 2016 Juan Pablo Risso <juano23@gmail.com>
Modified from code found here: https://www.hackster.io/juano2310/computer-vision-as-motion-sensor-for-smartthings-803341

Dependencies: python-twisted, cv2, pyimagesearch

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import argparse
import logging.handlers
import requests

from time import time
from twisted.web import server, resource
from twisted.internet import reactor
from twisted.internet.defer import succeed
from twisted.internet.protocol import DatagramProtocol
from twisted.web.iweb import IBodyProducer
from twisted.web._newclient import ResponseFailed
from zope.interface import implements

logger = logging.getLogger('MotionNotifySSDP')
hdlr = logging.handlers.RotatingFileHandler('/var/tmp/motion-notify-ssdp.log',
                                            maxBytes=1048576,
                                            backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

SSDP_PORT = 1900
SSDP_ADDR = '239.255.255.250'
UUID = 'b02c7058-fd87-4397-b8eb-96d64eb912f8'
SEARCH_RESPONSE = 'HTTP/1.1 200 OK\r\nCACHE-CONTROL:max-age=30\r\nEXT:\r\nLOCATION:%s\r\nSERVER:Linux, UPnP/1.0, Pi_Garage/1.0\r\nST:%s\r\nUSN:uuid:%s::%s'

def determine_ip_for_host(host):
    """Determine local IP address used to communicate with a particular host"""
    test_sock = DatagramProtocol()
    test_sock_listener = reactor.listenUDP(0, test_sock) # pylint: disable=no-member
    test_sock.transport.connect(host, 1900)
    my_ip = test_sock.transport.getHost().host
    test_sock_listener.stopListening()
    return my_ip

class SSDPServer(DatagramProtocol):
    """Receive and response to M-SEARCH discovery requests from SmartThings hub"""

    def __init__(self, interface='', status_port=0, device_target=''):
        self.interface = interface
        self.device_target = device_target
        self.status_port = status_port
        self.port = reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True) # pylint: disable=no-member
        self.port.joinGroup(SSDP_ADDR, interface=interface)
        reactor.addSystemEventTrigger('before', 'shutdown', self.stop) # pylint: disable=no-member

    def datagramReceived(self, data, (host, port)):
        try:
            header, _ = data.split('\r\n\r\n')[:2]
        except ValueError:
            return
        lines = header.split('\r\n')
        cmd = lines.pop(0).split(' ')
        lines = [x.replace(': ', ':', 1) for x in lines]
        lines = [x for x in lines if len(x) > 0]
        headers = [x.split(':', 1) for x in lines]
        headers = dict([(x[0].lower(), x[1]) for x in headers])

        logger.debug('SSDP command %s %s - from %s:%d with headers %s', cmd[0], cmd[1], host, port, headers)

        search_target = ''
        if 'st' in headers:
            search_target = headers['st']

        if cmd[0] == 'M-SEARCH' and cmd[1] == '*' and search_target in self.device_target:
            logger.info('Received %s %s for %s from %s:%d', cmd[0], cmd[1], search_target, host, port)
            url = 'http://%s:%d/status' % (determine_ip_for_host(host), self.status_port)
            response = SEARCH_RESPONSE % (url, search_target, UUID, self.device_target)
            self.port.write(response, (host, port))
        else:
            logger.debug('Ignored SSDP command %s %s', cmd[0], cmd[1])

    def stop(self):
        """Leave multicast group and stop listening"""
        self.port.leaveGroup(SSDP_ADDR, interface=self.interface)
        self.port.stopListening()

class StatusServer(resource.Resource):
    """HTTP server that serves the status of the camera to the
       SmartThings hub"""
    isLeaf = True

    def __init__(self, device_target, subscription_list, garage_door_status):
        self.device_target = device_target
        self.subscription_list = subscription_list
        self.garage_door_status = garage_door_status
        resource.Resource.__init__(self)

    def render_SUBSCRIBE(self, request): # pylint: disable=invalid-name
        """Handle subscribe requests from ST hub - hub wants to be notified of
           garage door status updates"""
        headers = request.getAllHeaders()
        logger.debug("SUBSCRIBE: %s", headers)
        if 'callback' in headers:
            cb_url = headers['callback'][1:-1]

            if not cb_url in self.subscription_list:
                self.subscription_list[cb_url] = {}
                #reactor.stop()
                logger.info('Added subscription %s', cb_url)
            self.subscription_list[cb_url]['expiration'] = time() + 24 * 3600

        return ""

    def render_GET(self, request): # pylint: disable=invalid-name
        #Handle updates to system status from device
        if request.path == '/status/status-active':
            self.notify_hubs("status-active")
            return ""
        elif request.path == '/status/status-inactive':
            self.notify_hubs("status-inactive")
            return ""
        #Handle requests for status from the Smartthings hub
        elif request.path == '/status':
            msg = '<msg><cmd>%s</cmd><usn>uuid:%s::%s</usn></msg>' % (self.garage_door_status['last_state'], UUID, self.device_target)
            logger.info("Polling request from %s for %s - returned %s",
                        request.getClientIP(),
                        request.path,
                        self.garage_door_status['last_state'])
            return msg
        else:
            logger.info("Invalid request from %s for %s",
                        request.getClientIP(),
                        request.path)
            return ""


    def notify_hubs(self, status):
        logger.info("Notifying...")
        """Notify the subscribed SmartThings hubs that a state change has occurred"""
        self.garage_door_status['last_state'] = status
        for subscription in self.subscription_list:
            if self.subscription_list[subscription]['expiration'] > time():
                logger.info("Notifying hub %s", subscription)
                msg = '<msg><cmd>%s</cmd><usn>uuid:%s::%s</usn></msg>' % (status, UUID, self.device_target)
                body = StringProducer(msg)
                logger.info("Notification message %s", msg)
                logger.info("Subscription %s", subscription)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                r = requests.post(subscription, data=body.body, headers=headers)

    def handle_response(self, response): # pylint: disable=no-self-use
        """Handle the SmartThings hub returning a status code to the POST.
           This is actually unexpected - it typically closes the connection
           for POST/PUT without giving a response code."""
        if response.code == 202:
            logger.info("Status update accepted")
        else:
            logger.error("Unexpected response code: %s", response.code)

    def handle_error(self, response): # pylint: disable=no-self-use
        """Handle errors generating performing the NOTIFY. There doesn't seem
           to be a way to avoid ResponseFailed - the SmartThings Hub
           doesn't generate a proper response code for POST or PUT, and if
           NOTIFY is used, it ignores the body."""
        if isinstance(response.value, ResponseFailed):
            logger.info("Response failed (expected)")
        else:
            logger.error("Unexpected response: %s", response)


class StringProducer(object):
    """Writes an in-memory string to a Twisted request"""
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer): # pylint: disable=invalid-name
        """Start producing supplied string to the specified consumer"""
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self): # pylint: disable=invalid-name
        """Pause producing - no op"""
        pass

    def stopProducing(self): # pylint: disable=invalid-name
        """ Stop producing - no op"""
        pass


def main():
    """Main function to handle use from command line"""

    arg_proc = argparse.ArgumentParser(description='Provides camera active/inactive status to a SmartThings hub')
    arg_proc.add_argument('--httpport', dest='http_port', help='HTTP port number', default=8080, type=int)
    arg_proc.add_argument('--deviceindex', dest='device_index', help='Device index', default=1, type=int)
    options = arg_proc.parse_args()

    device_target = 'urn:schemas-upnp-org:device:RPi_Computer_Vision:%d' % (options.device_index)

    subscription_list = {}
    camera_status = {'last_state': 'status-inactive'}

    # SSDP server to handle discovery
    SSDPServer(status_port=options.http_port, device_target=device_target)

    # HTTP site to handle subscriptions/polling
    status_site = server.Site(StatusServer(device_target, subscription_list, camera_status))
    reactor.listenTCP(options.http_port, status_site) # pylint: disable=no-member

    logger.info('Initialization complete')
    reactor.run() # pylint: disable=no-member

if __name__ == "__main__":
    main()
