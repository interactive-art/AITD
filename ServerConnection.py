#!/usr/bin/env python

import socket
import cPickle as pickle
import sys

HOST = 'localhost' # needs to be IP
PORT = 8887


class ServerConnection:

    def __init__(self):
    
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST , PORT))
        except socket.error, msg:
            print '!!! Error creating socket !!!'
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit();

        

        
        
    def send_points(self, points):
        try:
            self.socket.sendall(pickle.dumps(points))
        except socket.error:
            print 'Send failed'



sc = ServerConnection()


listOfPoints = []
listOfPoints.append( (1, 2))
listOfPoints.append( (2, 2))
listOfPoints.append( (3, 2))
listOfPoints.append( (4, 2))
listOfPoints.append( (5, 2))

sc.send_points(listOfPoints)


