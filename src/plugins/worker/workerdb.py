import os.path
import threading
from datetime import datetime

from sqlalchemy import Table, Column, MetaData, ForeignKey, PickleType, DateTime, String, Integer, Text, create_engine, select, and_, or_, not_, event
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base

import amsoil.core.pluginmanager as pm
import amsoil.core.log
logger=amsoil.core.log.getLogger('worker')


WORKERDB_PATH = pm.getService('config').get('worker.dbpath')
if not os.path.isabs(WORKERDB_PATH):
    from amsoil.config import ROOT_PATH
    WORKERDB_PATH = os.path.normpath(os.path.join(ROOT_PATH, WORKERDB_PATH))
WORKERDB_ENGINE = "sqlite:///%s" % (WORKERDB_PATH,)

# initialize sqlalchemy
db_engine = create_engine(WORKERDB_ENGINE, pool_recycle=6000)
db_Session = scoped_session(sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False))
Base = declarative_base()    

class JobDBEntry(Base):
    __tablename__ = 'worker_jobs'
    id = Column(Integer, primary_key=True)
    service_name = Column(String)
    callable_attr_str = Column(String)
    params = Column(PickleType)
    recurring_interval = Column(Integer)
    next_execution = Column(DateTime)

Base.metadata.create_all(db_engine)

def dbsession():
	"""This method returns a (new) sqlalchemy database session needed to perform actions on the database.
	If you want to query the database, it is ok to create new sessions for each query. If you want to change database entries, you need to hold on to the session until you commited the queries."""
    # db_metadata.create_all(db_engine) # always check if the database has been created. sqlalchemy does nothing if the schema has been created. This not so nicely implemented.
	threadlocal = threading.local()
	session = getattr(threadlocal, '_worker_dbsession', None)
	if session is None:
		session = db_Session()
		setattr(threadlocal, '_worker_dbsession', session)
	return session

def getAllJobs():
    """Do not change the values of the records retrieved with this function. You might accedently change them in the database too. Unless you call updateJob"""
    db = dbsession()
    records = db.query(JobDBEntry).all()
    return records

def addJob(job_db_entry):
    """Creates a config item, if it does not exist. If it already exists this function does not change anything."""
    db = dbsession()
    job_db_entry.id = None
    db.add(job_db_entry)
    db.commit()

def updateJobs():
    db = dbsession()
    db.commit()
    
def delJob(job_db_entry):
    db = dbsession()
    db.delete(job_db_entry)
    db.commit()
