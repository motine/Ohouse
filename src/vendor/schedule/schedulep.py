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
    
    Please create one instance of this class for each schedule_subject.
    What is a schedule_subject? There is one schedule for each resource classification/type.
    Conceptionally, two different subjects mean distinct databases.
    Example:
    find... -> 2 results
    find... -> 1 result
    
    Describe resource_id (e.g. the IP as string) to later find the record for a specific resource (e.g. IP).
    
    The schedule plugin can be used in two ways.
    - Either as best-effort booking system, which can not handle future reservations, but only reservations starting from now.
    - Or it can be used as pre-booking reservation system. In the latter case, the {start_time} parameter can be given to methods.
    
    Reservation booking constraints:
    - There shall never be _two_ reservations for the same subject and resource_id at any given time.
      Examples (pseudocode):
      ipSchedule = Schedule("IP")
      vmSchedule = Schedule("VM")
      ipSchedule.reserve(..., '192.168.10.1', datetime.utcnow())
      ipSchedule.reserve(..., '192.168.10.1', datetime.utcnow()) # ERROR
    
    Reservation value objects:
    Are of class AttributeDict. Behave like dicts but the keys can also be accessed/mutated as properties.
    You can use the str() method to see all info about one reservation.
    Example:
    
    The following parameters are parameters to methods of this class:
    - reservation_id (int) managed internally, can be used to identify specific a reservation record.
    - resource_id str (should be string)
    - resource_spec pickle, optional (should be a dict), can be nested but please do not include objects (except you are sure how pickle serialization works)
    - user_id str, optional
    - slice_id str, optional (can be empty, slice's name, a uuid, or however you distiguish experiments)
    - start_time datetime, optional (defaults to `utcnow()`)
    - end_time datetime, optional (init's {default_duration} (number in seconds) If no {end_time} is given in subsequent methods, this value will be added to the {start_time} to get the end of the reservation.)
    
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
    def __init__(self, schedule_subject, default_duration):
        """
        There is one schedule for each subject (resource classification/type). 
        {schedule_subject} This paramenter limits the scope of this class to the given subject (see above).
        {default_duration} (number in seconds) If no {end_time} is given in subsequent methods, this value will be added to the {start_time} to get the end of the reservation.
        """
        self.schedule_subject = schedule_subject
        self.default_duration = default_duration

    @serviceinterface
    def reserve(self, resource_id, resource_spec=None, slice_id=None, user_id=None, start_time=None, end_time=None):
        """
        Creates a reservation.
        Raises an ScheduleOverbookingError if there is already an entry for the given subject, resource_id and time (see constraints above).
        Returns the reservation id.

        Please see class description for info on parameters.
        """
        if start_time == None:
            start_time = datetime.utcnow()
        if end_time == None:
            end_time =  start_time + timedelta(0, self.default_duration)

        if len(self.find(resource_id=resource_id, start_time=start_time, end_time=end_time)) > 0:
            raise sex.ScheduleOverbookingError(self.schedule_subject, resource_id, start_time, end_time)
        
        new_record = ReservationRecord(
            schedule_subject=self.schedule_subject, resource_id=resource_id,
            resource_spec=resource_spec,
            start_time=start_time, end_time=end_time,
            slice_id=slice_id, user_id=user_id)
        db_session.add(new_record)
        db_session.commit()
        db_session.expunge_all()
        return new_record.reservation_id
    
    @serviceinterface
    def find(self, reservation_id=None, resource_id=None, slice_id=None, user_id=None, start_time=None, end_time=None):
        """
        Returns a list of reservation value objects (see class description).
        If all parameters a None, all reservations for this schedule_subject will be returned.
        If given parameters are not-None the result will be filtered by the respective field.
        If multiple params are given the result will be reduced (conditions will be AND-ed).
        If {start_time} is given, {end_time} must be given and vice versa.
        If the times are given, all records which touch the given period will be returned
        
        Limitations:
        - This method can not be used to filter records with NULL fields. E.g. it is not possible to filter all records to the ones which have set user_id to NULL.
        """
        q = db_session.query(ReservationRecord)
        q = q.filter_by(schedule_subject=self.schedule_subject)
        if not reservation_id is None:
            q = q.filter_by(reservation_id=reservation_id)
        if not resource_id is None:
            q = q.filter_by(resource_id=resource_id)
        if not slice_id is None:
            q = q.filter_by(slice_id=slice_id)
        if not user_id is None:
            q = q.filter_by(user_id=user_id)

        if (start_time is None) ^ (end_time is None):
            raise ValueError("If start_time is given, end_time must be given and vice versa.")
        if (not start_time is None) and (not end_time is None):
            q = q.filter(not_(or_(ReservationRecord.end_time < start_time, ReservationRecord.start_time > end_time)))

        records = q.all()
        result = [self._convertRecordtoValueObject(r) for r in records]
        db_session.expunge_all()
        return result

    def update(self, reservation_id, resource_id=None, resource_spec=None, slice_id=None, user_id=None, start_time=None, end_time=None):
        """
        Finds the reservation by its {reservation_id} and updates the fields by the given parameters.
        If a parameter is None, the field will be left unchanged.
        Raises ScheduleNoSuchReservationError if there is no such reservation.
        Returns the changed reservation as value object (see class description).
        
        Limitation:
        - It is not possible make a field None/NULL with this method, because the None parameter will be interpreted as 'please leave unchanged'.
        """
        reservation = self._find_reservation(reservation_id)
        # this could be done shorter with setattr, but I rather have it expicit
        if not resource_id is None:
            reservation.reservation_id = reservation_id
        if not resource_spec is None:
            reservation.resource_spec = resource_spec
        if not slice_id is None:
            reservation.slice_id = slice_id
        if not user_id is None:
            reservation.user_id = user_id
        if not start_time is None:
            reservation.start_time = start_time
        if not end_time is None:
            reservation.end_time = end_time
        db_session.commit()
        db_session.expunge_all()
        return self._convertRecordtoValueObject(reservation)

    def cancel(self, reservation_id):
        """
        Removes the reservation with the given id.
        Raises ScheduleNoSuchReservationError if there is no such reservation.
        Returns the values of the removed object as value object (see class description).
        """
        reservation = self._find_reservation(reservation_id)
        result = self._convertRecordtoValueObject(reservation)
        db_session.delete(reservation)
        db_session.commit()
        db_session.expunge_all()
        return result

    def _find_reservation(self, reservation_id):
        try:
            return db_session.query(ReservationRecord).filter_by(schedule_subject=self.schedule_subject).filter_by(reservation_id=reservation_id).one()
        except MultipleResultsFound, e: # this should never happen, because reservation_id is the primary key in the database
            raise RuntimeError("There are multiple primary keys %d" % (reservation_id,))
        except NoResultFound, e:
            raise sex.ScheduleNoSuchReservationError(reservation_id)

    def _convertRecordtoValueObject(self, db_record):
        """Converts a given database record to a value object (see class description)."""
        result_dict = {c.name: getattr(db_record, c.name) for c in db_record.__table__.columns}
        del result_dict['schedule_subject']
        return AttributeDict(result_dict)

# ----------------------------------------------------
# ------------------ database stuff ------------------
# ----------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime, PickleType, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import and_, or_, not_

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
    
    schedule_subject = Column(String(255))
    resource_id = Column(String(255))
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    slice_id = Column(String(255))
    user_id = Column(String(255))
    
    resource_spec = Column(PickleType())

DB_Base.metadata.create_all(DB_ENGINE) # create the tables if they are not there yet