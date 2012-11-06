#!/usr/bin/env python

import socket
import cPickle as pickle
import sys


class ServerConnection:

    def __init__(self, host, port):
    
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host , port))
        except socket.error, msg:
            print '!!! Error creating socket !!!'
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit();

        

    def send_resolution(self, width, height):
        try:
            self.socket.sendall(pickle.dumps(( width,height )))
        except socket.error:
            print 'send_resolution failed'
            sys.exit();
        
        
    def send_points(self, points):
        try:
            self.socket.sendall(pickle.dumps(points))
        except socket.error:
            print 'Send failed'



