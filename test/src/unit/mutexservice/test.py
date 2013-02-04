import os
import threading  
import time 
import sys
from os.path import dirname, join, normpath

PYTHON_DIR = normpath(join(dirname(__file__), '../../../../src/'))
sys.path.insert(0,PYTHON_DIR)

from amsoil.core.mutex import MutexService
SCOPE_NAME="test"
 
class MyThreadWith(threading.Thread):  
    def __init__(self,num):
        threading.Thread.__init__(self)
        self.__num = str(num) 
    def run(self):  
        print "Starting Thread #"+self.__num
        with MutexService.mutex(SCOPE_NAME): 
            print "Within MUTEX zone. Thread #"+self.__num
            time.sleep(int(self.__num))
        print "Leaving MUTEX zone. Thread #"+self.__num

class MyThread(threading.Thread):  
    def __init__(self,num):
        threading.Thread.__init__(self)
        self.__num = str(num) 
    def run(self):  
        print "Starting Thread #"+self.__num
        MutexService.lock(SCOPE_NAME)
        print "Within MUTEX zone. Thread #"+self.__num
        time.sleep(int(self.__num))
        MutexService.unlock(SCOPE_NAME)
        print "Leaving MUTEX zone. Thread #"+self.__num


##
t1 = MyThread(1)
t2 = MyThread(2)
t1.start()
t2.start() 

##with test
t1 = MyThreadWith(3)
t2 = MyThreadWith(4)
t1.start()
t2.start() 

