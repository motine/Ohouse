import os
import sys
from os.path import dirname, join, normpath

PYTHON_DIR = normpath(join(dirname(__file__), '../../../../src/'))
sys.path.insert(0,PYTHON_DIR)
PYTHON_DIR = normpath(join(dirname(__file__), '../../../../src/plugins/core_resourcemanagerregistry/'))
sys.path.insert(0,PYTHON_DIR)
print sys.path

from rmr.resourcemanagerregistry import ResourceManagerRegistry
from rmr.base.resourcemanager import ResourceManager
from rmr.base.resource import Resource


class R(object):
    pass
class M(Resource):
    def start():
        pass 
    def getOperationalState():
        pass 
    
class T(Resource):
    def start():
        pass 
    def getOperationalState():
        pass 

class RM1(ResourceManager):
    def temporallyReserve():
        pass
    def reserve():
        pass
    def updateReserve():
        pass
    def release():
        pass


class RM2(ResourceManager):
    def temporallyReserve():
        pass
    def reserve():
        pass
    def updateReserve():
        pass
    def release():
        pass


############
###Testing##
############
  
reg = ResourceManagerRegistry()

rm1=RM1([T])
print "Registering Test..."
reg.register(rm1)

print "Trying to register a new Test.."
reg.register(RM1([M]))
reg.register(RM2([M,T]))

print "Getting al RM..."
for rm in reg.retrieve():
    print "Got"+str(rm)

print "Getting al RM dealing with Resources M..."
for rm in reg.retrieve(M):
    print "Got"+str(rm)


print "Unregistering Test..."
reg.unRegister(rm1)
