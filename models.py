import datetime
from google.appengine.ext import db

# data models
class Eatery(db.Model):
    RestaurantName = db.StringProperty(required = True)
    CuisineType = db.StringProperty()
    City = db.StringProperty()
    State = db.StringProperty()
    NotesComments = db.StringProperty()
    Completed = db.BooleanProperty()
    FirstTripDate = db.DateProperty()
    LastVisitDate = db.DateProperty()
    NumberOfTrips = db.IntegerProperty()
    DaysSinceLastTrip = db.IntegerProperty()
    P1Rating = db.IntegerProperty()
    P2Rating = db.IntegerProperty()
    AverageRating = db.FloatProperty()
    YelpBusinessID = db.StringProperty()
    StreetAddress = db.StringProperty()
    ZipCode = db.IntegerProperty()

    @classmethod
    def by_id(cls,eid,couple_key,keys_only):
        e = cls.get_by_id(eid,parent=couple_key)
        return e

    def calc_days_since_last_trip(self):
        date_offset = datetime.date.today() - self.LastVisitDate
        return date_offset.days

class Couple(db.Model):
    P1 = db.StringProperty(required = True)
    P1Email = db.StringProperty()
    P1Nickname = db.StringProperty()
    P2 = db.StringProperty()
    P2Email = db.StringProperty(required=True)
    P2Nickname = db.StringProperty()

    @classmethod
    def by_P2Email(cls, p2_email):
        sub = cls.all().filter('P2Email =', p2_email).get()
        return sub

    @classmethod
    def by_user_id(cls,user_id,parent_key=None,keys_only=False):
        couple = cls.all(keys_only=keys_only).filter('P1 =', user_id).get()
        if not couple:
            couple = cls.all(keys_only=keys_only).filter('P2 =', user_id).get()
        return couple

class Trip(db.Model):
    LocationID = db.IntegerProperty(required = True)
    Type = db.StringProperty(required = True)
    Date = db.DateProperty(required = True)

    @classmethod
    def by_location_id(cls,location_id,parent_key=None,keys_only=False):
        trip = cls.all(keys_only=keys_only).filter('LocationID =', location_id).get()        
        return trip