#!/usr/bin/python3

# Author(s): Luiz Felipe Vecchietti, Chansol Hong
# Maintainer: Chansol Hong (cshong@rit.kaist.ac.kr)
# Description: Program that receives and executes a given command from a remote simulator

######################################################
#   Input the path to the player program to be run   #
######################################################
executable = "./player_rulebased-A_py/player_rulebased-A.py"

######################################################
#                 Input the datapath                 #
######################################################
datapath = "./team_a_data"

import sys
import subprocess

from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from twisted.internet import reactor

class PlayerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Game request from: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        cmd_segment = payload.decode('utf8')

        command = executable + " " + cmd_segment + " " + datapath

        self.popen_in_thread(
            lambda line: reactor.callFromThread(
            lambda: self.sendMessage(line)
            ),
            command
            )

    def popen_in_thread(self, callback, command):
        def threaded():
            a = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
            for line in iter(a.stdout.readline, b''):
                callback(line)
            if (a.wait() == 0):
                self.sendClose()
            elif (a.wait() > 0):
                output, error = a.communicate()
                self.sendMessage(error)
                self.sendClose()
        reactor.callInThread(threaded)

    def onClose(self, wasClean, code, reason):
        print("Connection with simulator closed: {0}".format(reason))

class PlayerServerFactory(WebSocketServerFactory):
    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)

if __name__ == '__main__':
    factory = PlayerServerFactory(u"ws://127.0.0.1:51235")
    factory.protocol = PlayerProtocol
    factory.setProtocolOptions(maxConnections=2)

    print("Listening to game requests...")
    reactor.listenTCP(51235, factory)
    reactor.run()
