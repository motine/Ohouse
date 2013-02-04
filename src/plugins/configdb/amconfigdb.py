from sqlalchemy import (Table, Column, MetaData, ForeignKey, PickleType, String,
                                                Integer, Text, create_engine, select, and_, or_, not_,
                                                event)
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base

import threading

from amsoil.config import (CONFIGDB_PATH, CONFIGDB_ENGINE)
from amsoil.core.exception import CoreException
from amsoil.core import serviceinterface
import amsoil.core.pluginmanager as pm

import amsoil.core.log
logger=amsoil.core.log.getLogger('configdb')

# initialize sqlalchemy
db_engine = create_engine(CONFIGDB_ENGINE, pool_recycle=6000)
db_Session = scoped_session(sessionmaker(autoflush=True, bind=db_engine, expire_on_commit=False))
Base = declarative_base()    
class ConfigEntry(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(PickleType)
    desc = Column(Text)
Base.metadata.create_all(db_engine)

def dbsession():
	"""This method returns a (new) sqlalchemy database session needed to perform actions on the database.
	If you want to query the database, it is ok to create new sessions for each query. If you want to change database entries, you need to hold on to the session until you commited the queries."""
    # db_metadata.create_all(db_engine) # always check if the database has been created. sqlalchemy does nothing if the schema has been created. This not so nicely implemented.
	threadlocal = threading.local()
	session = getattr(threadlocal, '_config_dbsession', None)
	if session is None:
		session = db_Session()
		setattr(threadlocal, '_config_dbsession', session)
	return session

# exceptions
class UnknownConfigKey(CoreException):
    def __init__ (self, key):
        super(UnknownConfigKey, self).__init__()
        self.key = key
    def __str__ (self):
        return "Unknown config key '%s'" % (self.key)

class DuplicateConfigKey(CoreException):
    def __init__ (self, key):
        super(DuplicateConfigKey, self).__init__()
        self.key = key
    def __str__ (self):
        return "Duplicate config key '%s'" % (self.key)

class ConfigDB:
    def _getRow(self, db, key):
        try:
            return db.query(ConfigEntry).filter_by(key=key).one()
        except MultipleResultsFound:
            raise DuplicateConfigKey(key)
        except NoResultFound:
            raise UnknownConfigKey(key)
        
    
    @serviceinterface
    def install(self, key, defaultValue, defaultDescription):
        """Creates a config item, if it does not exist. If it already exists this function does not change anything."""
        db = dbsession()
        try:
            self._getRow(db, key)
        except UnknownConfigKey:
            record = ConfigEntry(key=key, value=defaultValue, desc=defaultDescription)
            db.add(record)
            db.commit()
        return
    
    @serviceinterface
    def set(self, key, value):
        db = dbsession()
        res = self._getRow(db, key)
        res.value = value
        db.commit()
    
    @serviceinterface
    def get(self, key):
        db = dbsession()
        return self._getRow(db, key).value

    @serviceinterface
    def getAll(self):
        """
        Lists all config items available in the database.
        Returns a list of hashes. Each hash has the following keys set: key, value, description."""
        db = dbsession()
        records = db.query(ConfigEntry).all()
        return [{'key':r.key, 'value':r.value, 'description':r.desc} for r in records]


# Nick's old code, see old import2012 branch