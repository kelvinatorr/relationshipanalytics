import webapp2
import jinja2
import os
import csv
import datetime

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import db

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
        process_csv(blob_info)
 
        blobstore.delete(blob_info.key())  # optional: delete file after import
        self.redirect("/")
    
 
# helper functions
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

def process_csv(blob_info):
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
    				)
        # date, data, value = row
        entry = HitList(**r)
        entry.put()

def int_or_null(data):
    if data != '':
        return int(data)
    else:
        return None

# data models
class HitList(db.Model):
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

class Couple(db.Model):
    p1 = db.StringProperty(required = True)
    p2 = db.StringProperty()


#url handlers
class MainPage(BaseHandler):
    def get(self):
        self.write(self.user.nickname())
        # self.render('index.html')





application = webapp2.WSGIApplication([
    ('/',MainPage)
   ,('/upload',Upload)   
], debug=True)
