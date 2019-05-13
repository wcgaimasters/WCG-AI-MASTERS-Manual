#!/usr/bin/python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)
# Description: Program that relays execution command to a remote computer

import sys
import argparse

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

from twisted.internet import reactor

##################################################################
# Input the IP of the computer where the Webots program will run #
##################################################################
simulator_ip = "127.0.0.1"

##################################################################
# Input the IP of the computer where the player program will run #
##################################################################
player_ip = "127.0.0.1"


class SimulatorClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        #print("WebSocket connection open.")

        self.sendMessage(self.factory.command.encode('utf8'))

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Error: Binary message received: {0} bytes".format(len(payload)))
        else:
            print(payload.decode('utf8').rstrip('\n'))
            sys.__stdout__.flush()

    def onClose(self, wasClean, code, reason):
        #print("WebSocket connection closed: {0}".format(reason))
        if reactor.running:
            reactor.stop()

class SimulatorClientFactory(WebSocketClientFactory):

    def __init__(self, url, command):
        WebSocketClientFactory.__init__(self, url)
        self.command = command

if __name__ == '__main__':

    try:
        unicode
    except NameError:
        # Define 'unicode' for Python 3
        def unicode(s, *_):
            return s

    def to_unicode(s):
        return unicode(s, "utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("server_ip", type=to_unicode)
    parser.add_argument("port", type=to_unicode)
    parser.add_argument("realm", type=to_unicode)
    parser.add_argument("key", type=to_unicode)
    parser.add_argument("datapath", type=to_unicode)

    args = parser.parse_args()

    command = simulator_ip + " " + \
              args.port + " " + args.realm + " " +  args.key + " "

    factory = SimulatorClientFactory(u"ws://127.0.0.1:51235", command)
    factory.protocol = SimulatorClientProtocol

    reactor.connectTCP(player_ip, 51235, factory)
    reactor.run()
