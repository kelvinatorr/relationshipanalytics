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
        key = "Couple_Key|" + self.user.user_id()
        couple_key = cache_entity(key,self.user.user_id(),None,Couple.by_user_id,keys_only=True)
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
        key = "Couple_Key|" + self.user.user_id()
        couple_key = cache_entity(key,self.user.user_id(),None,Couple.by_user_id,keys_only=True)
        # Get the user's Couple's key       
        # couple_key = Couple.by_user_id(self.user.user_id(),keys_only=True)
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

    def post(self):
        search_button = self.request.get('search')
        # Check which button was pressed by the user.
        if search_button:
            key = "Couple_Key|" + self.user.user_id()
            couple_key = cache_entity(key,self.user.user_id(),None,Couple.by_user_id,keys_only=True)
            if couple_key:                
                search_attribute = self.request.get('attribute')
                allowed_attributes = set(['RestaurantName','City','State','CuisineType'])
                # Check that requested attribute is valid.
                if search_attribute in allowed_attributes:
                    search_string = self.request.get('search_string').upper()                    
                    url_search = search_attribute + "=" + search_string
                    self.redirect('/?filter=TRUE&%s' %url_search)
                else:
                    self.render('index.html', error_search='Invalid attribute selected!')
            else:
                self.redirect('/register')

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
                # Go through dictionary of filters, if a property of the entity doesn't match a filter do not include in result.
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

class EditHitlist(BaseHandler):
    def get(self):
        key = "Couple|" + self.user.user_id()
        couple = cache_entity(key,self.user.user_id(),None,Couple.by_user_id,keys_only=False)
        if couple:
            eatery_id = self.request.get("id")
            if eatery_id:
                if eatery_id.isnumeric():
                    eatery_id = int(eatery_id)
                    found = self.check_hitlist(couple.key(), eatery_id)
                    if found:
                        # Get cache eatery
                        key = 'Eatery|' + str(eatery_id)
                        eatery = cache_entity(key,eatery_id,couple.key(),Eatery.by_id)
                        self.render('hitlist-edit.html',eatery=eatery,couple=couple)
                    else:
                        self.error(403)
                elif eatery_id.upper() == "NEW":
                    # Render html template for creating a new eatery.
                    self.render('hitlist-create.html',couple=couple)
                else:
                    self.redirect("/")
            else:
                self.redirect("/")
        else:
            # If user is not associated with a couple redirect to registration page.
            self.redirect('/register')

    def post(self):
        submit = self.request.get('submit')
        if submit:
            couple_memcache_key = "Couple_Key|" + self.user.user_id()
            couple_key = cache_entity(couple_memcache_key,self.user.user_id(),None,Couple.by_user_id,keys_only=True)
            if couple_key:
                eatery_id = self.request.get("id")
                if eatery_id: 
                    if eatery_id.isnumeric():                               
                        eatery_id = int(eatery_id)
                        # check if valid eatery id for the couple_key.
                        edit_found = self.check_hitlist(couple_key, eatery_id)
                        new = False
                    elif eatery_id.upper() == "NEW":
                        # User is posting data for new Eatery
                        edit_found = False
                        new = True
                    else:
                        # Fail the post attempt and 403 it.
                        edit_found = False
                        new = False

                    if edit_found or new:                        
                        # verify user inputs
                        failed = False
                        error_dict = {}
                        # Verify that the user entered a restaurant name.
                        restaurant_name = self.request.get("restaurantName")                        
                        if not restaurant_name:
                            failed = True
                            error_name = "You must enter a name."
                            error_dict['error_name'] = error_name
                        
                        cuisine_type = self.request.get("cuisineType")
                        city = self.request.get("city")
                        state = self.request.get("state")
                        notes_comments = self.request.get("notesComments")
                        completed = self.request.get("completed").upper()
                        if completed == "TRUE":
                            completed = True
                        else:
                            completed = False

                        first_trip_date = self.request.get("firstTripDate")
                        # Check if a value was entered first.
                        if first_trip_date:
                            first_trip_date = convert_string_to_date(first_trip_date)
                            if not first_trip_date:
                                failed = True
                                error_first_trip = "Invalid date format."
                                error_dict['error_first_trip'] = error_first_trip
                        else:
                            first_trip_date = None

                        last_visit_date = self.request.get("lastVisitDate")
                        # Check if a value was entered first.
                        if last_visit_date:
                            last_visit_date = convert_string_to_date(last_visit_date)
                            if not last_visit_date:
                                failed = True
                                error_last_visit = "Invalid date format."
                                error_dict['error_last_visit'] = error_last_visit
                        else:
                            last_visit_date = None

                        number_of_trips = self.request.get("numberOfTrips")
                        if number_of_trips and not number_of_trips.isnumeric():
                            failed = True
                            error_number_of_trips = "Invalid number entered."
                            error_dict['error_number_of_trips'] = error_number_of_trips
                        else:
                            number_of_trips = int(number_of_trips)

                        p1_Rating = self.request.get("p1Rating")
                        if p1_Rating:
                            check  = self.check_rating(1,p1_Rating)
                            if check[0]:
                                p1_Rating = int(p1_Rating)
                            else:
                                error_dict[check[1]] = check[2]
                        else:
                            p1_Rating = None

                        p2_Rating = self.request.get("p2Rating")
                        if p2_Rating:
                            check = self.check_rating(2,p2_Rating)
                            if check[0]:
                                p2_Rating = int(p2_Rating)
                            else:
                                error_dict[check[1]] = check[2]
                        else:
                            p2_Rating = None
                        # Get eatery entity.
                        if edit_found:
                            # handler for edits.
                            key = 'Eatery|' + str(eatery_id)
                            eatery = cache_entity(key,eatery_id,couple_key,Eatery.by_id)

                        if failed:
                            if edit_found:
                                # add eatery to render dictionary
                                error_dict['eatery'] = eatery
                            # get couple object
                            couple_memcache_key = "Couple|" + self.user.user_id()
                            couple = cache_entity(couple_memcache_key,self.user.user_id(),None,Couple.by_user_id,keys_only=False)
                            # add couple to render dictionary
                            error_dict['couple'] = couple
                            if edit_found:
                                # render edit template for edits.
                                self.render('hitlist-edit.html',**error_dict)
                            else:
                                # Render create template for creates.
                                self.render('hitlist-create.html',**error_dict)
                        else:
                            # User inputs validated prepare to commit to
                            days_last_trip = 0
                            # Calculate average rating.
                            if p1_Rating and p2_Rating:
                                average_rating = (p1_Rating + p2_Rating) / 2.0
                            elif p1_Rating:
                                average_rating = float(p1_Rating)
                            elif p2_Rating:
                                average_rating = float(p2_Rating)
                            else:
                                average_rating = None
                            
                            # change eatery entry to reflect changes.
                            if edit_found:
                                eatery.RestaurantName = restaurant_name
                            else:
                                # Or create new entity.
                                eatery = Eatery(RestaurantName=restaurant_name,parent=couple_key)

                            eatery.CuisineType = cuisine_type
                            eatery.City = city
                            eatery.State = state
                            eatery.NotesComments = notes_comments
                            eatery.Completed = completed
                            eatery.FirstTripDate = first_trip_date
                            eatery.LastVisitDate = last_visit_date
                            eatery.NumberOfTrips = number_of_trips
                            eatery.P1Rating = p1_Rating
                            eatery.P2Rating = p2_Rating
                            eatery.AverageRating = average_rating

                            # Save new Eatery to DB
                            eatery.put()
                            if new:
                                eatery_id = eatery.key().id()
                                key = 'Eatery|' + str(eatery_id)
                                hitlist_key = "Hitlist|" + str(couple_key.id())
                                hitlist_cache(hitlist_key,couple_key,update=True)
                            # refresh memcache
                            eatery = cache_entity(key,eatery_id,couple_key,Eatery.by_id,update=True)
                            # Redirect to hitlist.
                            self.redirect("/")
                    else:
                        self.error(403)
                else:
                    self.redirect("/")
            else:
                self.redirect("/register")

    def check_rating(self,person,rating):
        """
        Checks if the user entered rating is a number from 0 to 5.
        Returns the key for the error dictionary and error message if False.
        """
        valid = True
        if rating.isnumeric():
            rating = int(rating)
            print rating
            if rating > 5 or rating < 0:
                valid = False
                error_key = 'error_p%s_rating' % person
                error_message = "Please enter a number between 0 and 5"
        else:
            valid = False
            error_key = 'error_p%s_rating' % person
            error_message = "Please enter a valid number between 0 and 5"
        if valid:
            return valid,None,None
        else:
            return valid,error_key,error_message

    def check_hitlist(self,couple_key,eatery_id):
        """ Checks that a given eatery id is in the couple's hitlist"""
        hitlist_key = "Hitlist|" + str(couple_key.id())
        # Get a list of Entity keys that are associated with this user.
        hitlist_keys = hitlist_cache(hitlist_key,couple_key)
        # Loop through hitlist to make sure that the requested Eatery is in their hitlist.
        found = False
        for e_key in hitlist_keys:            
            if e_key.id() == eatery_id:
                found = True
                break
        return found

class Test(BaseHandler):
    def get(self):
        self.render("test.html")


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

def cache_entity(key,query_key,parent_key,entity_query_function,keys_only=False,update=False):
    obj = memcache.get(key)    
    if not obj or update:        
        logging.error('User query for' + key)       
        # entity query function must return the actual object!
        obj = entity_query_function(query_key,parent_key,keys_only)        
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

#url handlers

application = webapp2.WSGIApplication([
    ('/',MainPage)
   ,('/upload',Upload)   
   ,('/register',Register)
   ,('/confirm',Confirm)
   ,('/edit',EditHitlist)
   ,('/test',Test)
], debug=True)
