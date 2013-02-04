import os
import threading  
import time 
import sys
import logging 
from os.path import dirname, join, normpath

PYTHON_DIR = normpath(join(dirname(__file__), '../../../../src/'))
sys.path.insert(0,PYTHON_DIR)

from amsoil.core.ipc import IPC

logging.basicConfig(level=logging.DEBUG)

def receive(ch, method, properties, body):
    print "[x] Received %r" % (body,)

QUEUE="myQueue"

def initQueues():
    IPC.destroyQueue(QUEUE)
    #try:
    #Test create and destroy
    IPC.createQueue(QUEUE)
    time.sleep(5)

    IPC.destroyQueue(QUEUE)
    time.sleep(5)

    IPC.createQueue(QUEUE)
    time.sleep(5)

#Register receiver
#initQueues()

IPC.registerReceiver(QUEUE,receive)

#Sending something
for i in range(5):
    IPC.send(QUEUE,"Hola")
    time.sleep(2)

time.sleep(5)

IPC.unregisterReceiver(QUEUE,receive)
#except Exception as e:
#    print str(e)
