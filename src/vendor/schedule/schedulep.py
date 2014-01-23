from datetime import datetime, timedelta

from amsoil.core import pluginmanager as pm
from amsoil.core import serviceinterface
from amsoil.core.exception import CoreException
from amsoil.config import expand_amsoil_path

import amsoil.core.log
logger=amsoil.core.log.getLogger('schedule')

import scheduleexceptions as sex
from attributedict import AttributeDict

class Schedule(object):
    """
    
    Please create one instance of this class for each resource classification.
    What is a resource classification? There is one schedule for each resource classification/type.
    Conceptionally, two different classifications mean distinct databases.
    Example:
    find... -> 2 results
    find... -> 1 result
    
    Describe resource_id (e.g. the IP as string) to later find the record for a specific resource (e.g. IP).
    
    The schedule plugin can be used in two ways.
    - Either as best-effort booking system, which can not handle future reservations, but only reservations starting from now.
    - Or it can be used as pre-booking reservation system. In the latter case, the {start_time} parameter can be given to methods.
    
    Reservation booking constraints:
    - There shall never be _two_ reservations for the same resource_classification and resource_id at any given time.
      Examples (pseudocode):
      ipSchedule = Schedule("IP")
      vmSchedule = Schedule("VM")
      ipSchedule.reserve(..., '192.168.10.1', datetime.utcnow())
      ipSchedule.reserve(..., '192.168.10.1', datetime.utcnow()) # ERROR
    
    Reservation value objects:
    Are of class AttributeDict. Behave like dicts but the keys can also be accessed/mutated as properties.
    Example:
    
    The following parameters are parameters to methods of this class:
    - reservation_id (int) managed internally, can be used to identify specific a reservation record.
    - resource_id (should be string)
    - resource_spec optional (should be a dict), can be nested but please do not include objects (except you are sure how pickle serialization works)
    - user_id optional
    - slice_name optional
    - start_time optional (defaults to `utcnow()`)
    - end_time optional (init's {default_duration} (number in seconds) If no {end_time} is given in subsequent methods, this value will be added to the {start_time} to get the end of the reservation.)
    
    For specifying time always use the pyhton class datetime. UTC is assumed as timezone.
    
    TODO
    - create wiki page for documentation
    - create slides for documentation
    - What happens with expiry?
    
    NOTE:
    This class will never deliver a Database record to the outside.
    It will copy the contents of the database record, so the plugin user can not accidentally change the database.
    For problem statement see https://github.com/fp7-ofelia/AMsoil/wiki/Persistence#expunge
    """
    
    @serviceinterface
    def __init__(self, resource_classification, default_duration):
        """
        There is one schedule for each resource classification/type. 
        {resource_classification} This paramenter limits the scope of this class to the given classification (see above).
        {default_duration} (number in seconds) If no {end_time} is given in subsequent methods, this value will be added to the {start_time} to get the end of the reservation.
        """
        self.resource_classification = resource_classification
        self.default_duration = default_duration

    @serviceinterface
    def reserve(self, resource_id, resource_spec=None, slice_name=None, user_id=None, start_time=None, end_time=None):
        """
        Creates a reservation.
        Raises an ScheduleOverbookingError if there is already an entry for the given classification, resource_id and time (see constraints above).
        Returns the reservation id

        Please see class description for info on parameters.
        
        """
        if start_time == None:
            start_time = datetime.utcnow()
        if end_time == None:
            end_time =  start_time + timedelta(0, self.default_duration)

        if len(self.reservations_for(resource_id=resource_id, start_time=start_time, end_time=end_time)) > 0:
            raise sex.ScheduleOverbookingError(self.resource_classification, resource_id, start_time, end_time)
        
        new_record = ReservationRecord(
            classification=self.resource_classification, resource_id=resource_id,
            resource_spec=resource_spec,
            start_time=start_time, end_time=end_time,
            slice_name=slice_name, user_id=user_id)
        db_session.add(new_record)
        db_session.commit()
        db_session.expunge_all()
        return new_record.reservation_id
    
    @serviceinterface
    def reservations_for(self, reservation_id=None, resource_id=None, resource_spec=None, slice_name=None, user_id=None, start_time=None, end_time=None):
        """
        Returns a list of reservation value objects (see class description).
        If all parameters a None, all reservations for this resource_classification will be returned.
        If given parameters are not-None the result will be filtered by the respective field.
        If multiple params are given the result will be reduced (conditions will be AND-ed).
        
        Limitations:
        - This method can not be used to filter records with NULL fields. E.g. it is not possible to filter all records to the ones which have set user_id to NULL.
        """
        q = db_session.query(ReservationRecord)
        q.filter_by(classification=self.resource_classification)
        if not reservation_id is None:
            q.filter_by(reservation_id=reservation_id)
        records = q.all()
        result = [self._convertRecordtoValueObject(r) for r in records]
        return result

    def _convertRecordtoValueObject(self, db_record):
        """Converts a given database record to a value object (see class description)."""
        return AttributeDict({c.name: getattr(db_record, c.name) for c in db_record.__table__.columns})

# ----------------------------------------------------
# ------------------ database stuff ------------------
# ----------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, PickleType, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists

from amsoil.config import expand_amsoil_path

# initialize sqlalchemy
DB_PATH = expand_amsoil_path(pm.getService('config').get('schedule.dbpath'))
DB_ENGINE = create_engine("sqlite:///%s" % (DB_PATH,)) # please see the wiki for more info
DB_SESSION_FACTORY = sessionmaker(autoflush=True, bind=DB_ENGINE, expire_on_commit=False)
db_session = scoped_session(DB_SESSION_FACTORY)
DB_Base = declarative_base() # get the base class for the ORM, which includes the metadata object (collection of table descriptions)

class ReservationRecord(DB_Base):
    """Encapsulates a record in the database."""
    __tablename__ = 'reservations'
    
    reservation_id = Column(Integer, primary_key=True)
    
    classification = Column(String(255))
    resource_id = Column(String(255))
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    slice_name = Column(String(255))
    user_id = Column(String(255))
    
    resource_spec = Column(PickleType())
    # @property
    # def available(self):
    #     return not bool(self.slice_name)

DB_Base.metadata.create_all(DB_ENGINE) # create the tables if they are not there yet