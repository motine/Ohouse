import time
import pickle

from amsoil.core import pluginmanager as pm
from amsoil.core import serviceinterface
import amsoil.core.log
logger=amsoil.core.log.getLogger('worker')

class WorkerServer(object):
    SLEEP_BETWEEN_CHECKS = 0.5 # seconds
    
    def __init__(self):
        super(WorkerServer, self).__init__()

    @serviceinterface
    def runServer(self):
        while True:
            print "checking for new jobs"
            
            # testing
            jobs = [{
                "service_name" : "dhcpresourcemanager",
                "callable_attr" : "test_remove_me",
                "params" : pickle.dumps(["a","b"])
            }]
            # end testing
            if len(jobs) > 0:
                job = jobs[0]
                del jobs[0]
                try:
                    service = pm.getService(job["service_name"])
                    params = pickle.loads(job["params"])
                    getattr(service, job["callable_attr"])(params)
                except Exception as e:
                    logger.error("Job terminated with exception: %s" % (e,))
            else:
                time.sleep(self.SLEEP_BETWEEN_CHECKS) # sec

class WorkerJob(object):
    @serviceinterface
    def addJob(self, job):
        # jobs.append(...)
        return None

    @serviceinterface
    def addScheduledJob(self, job, time):
        return None

    @serviceinterface
    def addRecurringJob(self, job, interval):
        return None
