from amsoil.core import pluginmanager as pm

from workers import WorkerServer, WorkerJob

def setup():
    worker_server = WorkerServer()
    pm.registerService('workerserver', worker_server)
    pm.registerService('workerjob', WorkerJob)
