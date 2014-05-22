import webapp2
import jinja2
import os
import csv
import datetime
import re
import logging
from time import sleep

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
#http handlers
class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
      t = jinja_env.get_template(template)
      return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def initialize(self, *a, **kw):        
        webapp2.RequestHandler.initialize(self, *a, **kw)
        user = users.get_current_user()
        if user:       
        	self.user = user
        else:
        	self.redirect(users.create_login_url(self.request.uri))

class Upload(BaseHandler,blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
 
        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url
 
        self.response.write(html_string)

    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        # Get the current user's Couple entity to set it as a ancestor for each entry in the csv.Dialect
        couple_key = Couple.by_user_id(self.user.user_id(),keys_only=True)
        process_csv(blob_info,couple_key)
        # Delete file after import
        blobstore.delete(blob_info.key())
        # Update Couple hitlist
        hitlist_key = "Hitlist|" + str(couple_key.id())
        hitlist_cache(hitlist_key,couple_key,update=True) 
        self.redirect("/")

class Register(BaseHandler):
    def get(self):
        self.render('register.html')

    def post(self):
        invite_email = self.request.get('invite_email')

        failed = False
        if not valid_username('username',invite_email):
            failed = True
            error_invite_email = 'Please enter a valid gmail address, including "@gmail.com"'

        if failed:
            self.render('register.html',invite_email=invite_email,error_invite_email=error_invite_email)
        else:            
            # Initialize new Couple entity. with P2Email as invite_email.
            couple = Couple(P1=self.user.user_id(),P1Email=self.user.email(),P1Nickname=self.user.nickname()
                            ,P2Email=invite_email)
            couple.put()
            self.write('Good job!')

class Confirm(BaseHandler):
    def get(self):
        # TODO:Check if email is in db. Entered by the inviter.
        # If yes then create new user entity. and update Couple class to have a value for p2 google_id        
        couple = Couple.by_P2Email(self.user.email())
        if couple:
            couple.P2 = self.user.user_id()
            couple.P2Nickname = self.user.nickname()
            couple.put()
            self.write('success %s!' % self.user.nickname())
        else:
            self.write('Your account is not associated with anyone. Would you like to create a new shared account?')

class MainPage(BaseHandler):
    def get(self):
        # self.write(self.user.nickname())
        # Get the user's Couple's key        
        couple_key = Couple.by_user_id(self.user.user_id(),keys_only=True)
        if couple_key:
            # get url arguments for filters
            filter_flag = self.request.get('filter')
            filters = None
            if filter_flag.upper() == 'TRUE':
                restaurant_name = self.request.get('RestaurantName')
                city = self.request.get('City')
                state = self.request.get('State')
                cuisine_type = self.request.get('CuisineType')
                filters = dict(RestaurantName=restaurant_name
                                ,City=city
                                ,State=state
                                ,CuisineType=cuisine_type)
            hitlist = self.get_hitlist(couple_key,filters)
            self.render('index.html',hitlist=hitlist)
        else:
            # If user is not associated with a couple redirect to registration page.
            self.redirect('/register')

    # def post(self):
    #     search_button = self.request.get('search')
    #     # Check which button was pressed by the user.
    #     if search_button:
    #         search_string = self.request.get('search_string').upper()
    #         couple_key = Couple.by_user_id(self.user.user_id(),keys_only=True)
    #         if couple_key:
    #             hitlist = self.get_hitlist(couple_key)
    #             # Loop through eateries in hitlist and attempt to match property RestaurantName with search_string
    #             result = []
    #             for e in hitlist:
    #                 if re.search(search_string,e.RestaurantName.upper()):
    #                     result.append(e)
    #             self.render('index.html',hitlist=result)
    #         else:
    #             self.redirect('/register')

    def get_hitlist(self,couple_key,filters):        
        hitlist_key = "Hitlist|" + str(couple_key.id())
        # Get a list of Entity keys that are associated with this user.
        hitlist_keys = hitlist_cache(hitlist_key,couple_key)
        # Build a list of Eatery entities to render.
        hitlist = []
        for e_key in hitlist_keys:
            key = 'Eatery|' + str(e_key.id())
            eatery = cache_entity(key,e_key.id(),couple_key,Eatery.by_id)
            if filters:
                match = True
                for f in filters:
                    if hasattr(eatery,f):
                        if filters[f] and not re.search(filters[f].upper(),getattr(eatery,f).upper()):
                            match = False
                            break
                if match:
                    hitlist.append(eatery)
            else:
                hitlist.append(eatery)
        return hitlist


# Memcache functions.
def hitlist_cache(key,couple_key,update=False):
    # Try to get list on Eatery entity keys from memcache
    hitlist = memcache.get(key)
    if not hitlist or update:        
        # Query all Eatery entities whose ancestor is the user's Couple
        hitlist_query = Eatery.all(keys_only=True).ancestor(couple_key)
        hitlist = list(hitlist_query)
        memcache.set(key,hitlist)
    return hitlist

def cache_entity(key,query_key,parent_key,entity_query_function,update=False):
    obj = memcache.get(key)    
    if not obj or update:        
        logging.error('User query for' + key)        
        # entity query function must return the actual object!
        obj = entity_query_function(query_key,parent_key)        
        memcache.set(key,obj)
    return obj

 
# helper functions
valid_dict = {'username':r"^[\S]+@gmail\.[\S]+$" 
              ,'password':r"^.{6,20}$"          
              }

def valid_username(string_type,target_string):
    regex = re.compile(valid_dict[string_type])
    return regex.match(target_string)

def convert_string_to_date(dateString):
    """
    Converts string date time to Python date object by trying multiple
    formats. Returns None if conversion failed
    """
    test_cases = ['%m/%d/%Y','%m/%d/%y', '%Y-%m-%d']
    res = None
    for f in test_cases:
        try:
            res = datetime.datetime.strptime(dateString, f).date()
            return res
        except:
            pass
    return res

def process_csv(blob_info,couple_key):
    blob_reader = blobstore.BlobReader(blob_info.key())
    reader = csv.reader(blob_reader, delimiter=',', quotechar='"')
    for row in reader:
        city_state = row[2].split(',')
        if row[11] == '':
            average_rating = None
        else:
            average_rating = float(row[11])

    	r = dict(RestaurantName = row[0]
					,CuisineType = row[1]
					,City = city_state[0].strip()
					,State = city_state[1].strip()
					,NotesComments = row[3]
					,Completed = bool(int(row[4]))
					,FirstTripDate = convert_string_to_date(row[5])
					,LastVisitDate = convert_string_to_date(row[6])
					,NumberOfTrips = int_or_null(row[7])
					,DaysSinceLastTrip = int_or_null(row[8])
					,P1Rating = int_or_null(row[9])
					,P2Rating = int_or_null(row[10])
					,AverageRating = average_rating
                    ,parent=couple_key
    				)        
        entry = Eatery(**r)
        entry.put()
        entry_id = entry.key().id()
        key = "Eatery|" + str(entry_id)
        # Add Eatery entry to memcache.
        cache_entity(key,entry_id,couple_key,Eatery.by_id,update=True)


def int_or_null(data):
    if data != '':
        return int(data)
    else:
        return None

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

    @classmethod
    def by_id(cls,eid,couple_key):
        e = cls.get_by_id(eid,parent=couple_key)
        return e

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
    def by_user_id(cls,user_id,keys_only=False):
        couple = cls.all(keys_only=keys_only).filter('P1 =', user_id).get()
        if not couple:
            couple = cls.all(keys_only=keys_only).filter('P2 =', user_id).get()
        return couple

#url handlers

application = webapp2.WSGIApplication([
    ('/',MainPage)
   ,('/upload',Upload)   
   ,('/register',Register)
   ,('/confirm',Confirm)
], debug=True)
