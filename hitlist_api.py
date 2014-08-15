import endpoints
import logging
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from time import sleep

import ra_memcache

from models import Eatery
from models import Couple

WEB_CLIENT_ID = '706028337645-oe249o4vs0lsm199561e6pdua98vk9ge.apps.googleusercontent.com'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID
package = 'hitlist'

class EateryMessage(messages.Message):
    restaurant_name = messages.StringField(1)
    cuisine_type = messages.StringField(2)
    city = messages.StringField(3)
    state = messages.StringField(4)
    notes_comments = messages.StringField(5)
    completed = messages.BooleanField(6)
    first_trip_date = message_types.DateTimeField(7)
    last_visit_date = message_types.DateTimeField(8)
    number_of_trips = messages.IntegerField(9)
    days_since_last_trip = messages.IntegerField(10)
    p1_rating = messages.FloatField(11)
    p2_rating = messages.FloatField(12)
    average_rating = messages.FloatField(13)
    yelp_business_id = messages.StringField(14)
    street_address = messages.StringField(15)
    zip_code = messages.IntegerField(16)    

class EateryNotes(messages.Message):
    restaurant_name = messages.StringField(1)
    notes_comments = messages.StringField(2)
    status_code = messages.IntegerField(3)

class EateryLocation(messages.Message):
    eatery_id = messages.IntegerField(1,variant=messages.Variant.INT64)
    restaurant_name = messages.StringField(2)    
    latitude = messages.FloatField(4)
    longitude = messages.FloatField(5)
    geocoded = messages.BooleanField(6)
    status_code = messages.IntegerField(7)

class EateryLocationCollection(messages.Message):
    """Collection of EateryLocations."""
    items = messages.MessageField(EateryLocation, 1, repeated=True)

@endpoints.api(name='hitlist',version='v1'
                ,allowed_client_ids=[WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID]
                ,audiences=[ANDROID_AUDIENCE]
                ,scopes=[endpoints.EMAIL_SCOPE])
class HelloWorldApi(remote.Service):
    """ hitlist API"""
    # pass
    ID_RESOURCE = endpoints.ResourceContainer(message_types.VoidMessage,id=messages.IntegerField(1,variant=messages.Variant.INT64))

    @endpoints.method(ID_RESOURCE, EateryNotes,path='eatery_notes/{id}', http_method='GET',name='eateries.getEateryNotes')
    def eatery_notes_get(self, request):
        status_code,couple_key = self.auth_api_user()
        if status_code == -2:
            raise endpoints.UnauthorizedException("Please sign in.")
        elif status_code == -1:
            return EateryNotes(status_code=-1)
        # Retreive the eatery
        key = 'Eatery|' + str(request.id)
        e = ra_memcache.cache_entity(key,request.id,couple_key,Eatery.by_id)
        # e = Eatery.by_id(request.id,couple_key,None)
        if e:                
            # Initialize the EateryMessage
            e_message = EateryNotes(restaurant_name=e.RestaurantName,notes_comments=e.NotesComments,status_code=0)                
            return e_message
        else:
            raise endpoints.NotFoundException('Eatery %s not found.' % request.id)

    @endpoints.method(ID_RESOURCE, EateryLocation,path='eatery_location/{id}', http_method='GET',name='eateries.getEateryLocation')
    def eatery_location_get(self, request):
        status_code,couple_key = self.auth_api_user()
        if status_code == -2:
            raise endpoints.UnauthorizedException("Please sign in.")
        elif status_code == -1:
            return EateryLocation(status_code=-1)
        # Retreive the eatery
        key = 'Eatery|' + str(request.id)
        e = ra_memcache.cache_entity(key,request.id,couple_key,Eatery.by_id)            
        if e:            
            # Check if this eatery has been geocoded.
            if e.Latitude and e.Longitude:
                geocoded = True
            else:
                geocoded = False
            # Initialize the EateryMessage                
            e_message = EateryLocation(restaurant_name=e.RestaurantName,latitude=e.Latitude
                ,longitude=e.Longitude,geocoded=geocoded,status_code=status_code)         
            return e_message
        else:
            raise endpoints.NotFoundException('Eatery %s not found.' % request.id)

    @endpoints.method(message_types.VoidMessage, EateryLocationCollection, path='eaterieslocation', http_method='GET',
                        name='eateries.getLocations')
    def locations_eateries_get(self,unused_request):
        status_code,couple_key = self.auth_api_user()
        if status_code == -2:
            raise endpoints.UnauthorizedException("Please sign in.")
        elif status_code == -1:
            return EateryLocation(status_code=-1)
        hitlist_key = "Hitlist|" + str(couple_key.key().id())
        # Get a list of Entity keys that are associated with this user.
        hitlist_keys = ra_memcache.hitlist_cache(hitlist_key,couple_key)
        geocoded_hitlist = []
        for e_key in hitlist_keys:
            key = 'Eatery|' + str(e_key.id())
            # Get the eatery entity from memcache and check if it has been geocoded.
            e = ra_memcache.cache_entity(key,e_key.id(),couple_key,Eatery.by_id)
            if e.Latitude and e.Longitude:
                # Form the EateryLocation Message.
                e_message = EateryLocation(restaurant_name=e.RestaurantName,latitude=e.Latitude
                                ,longitude=e.Longitude,geocoded=True,status_code=status_code) 
                geocoded_hitlist.append(e_message)
        return EateryLocationCollection(items=geocoded_hitlist)

    @endpoints.method(EateryLocation,EateryLocation,path='eatery_geocode',http_method='POST',name='eateries.geocode')
    def eatery_geocode_insert(self,request):
        status_code,couple_key = self.auth_api_user()
        if status_code == -2:
            raise endpoints.UnauthorizedException("Please sign in.")
        elif status_code == -1:
            return EateryLocation(status_code=-1)
        key = 'Eatery|' + str(request.eatery_id)
        eatery = ra_memcache.cache_entity(key,request.eatery_id,couple_key,Eatery.by_id)
        if eatery:
            eatery.Latitude = request.latitude
            eatery.Longitude = request.longitude
            eatery.put()
            # Refresh memcache
            eatery = ra_memcache.cache_entity(key,request.eatery_id,couple_key,Eatery.by_id,update=True)
        else:
            return EateryLocation(status_code=-2)
        return EateryLocation(status_code=0)

    def auth_api_user(self):
        current_user = endpoints.get_current_user()
        if not current_user:
            logging.error("Yup not signed in!!!")
            return -2,None
        else:
            # Get couple key
            key = "Couple_Key|" + current_user.email()
            couple_key = ra_memcache.cache_entity(key,current_user.email(),None,Couple.by_email,keys_only=False)                   
            # couple_key = Couple.by_email(current_user.email(),keys_only=True)
            if not couple_key:                
                return -1,None
            return 0,couple_key




APPLICATION = endpoints.api_server([HelloWorldApi])