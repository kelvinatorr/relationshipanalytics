import endpoints
import logging
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from time import sleep

import ra_memcache

from models import Eatery
from models import Couple

WEB_CLIENT_ID = '356591658043-r06nli81msv1s280plb91a2kjn25c02b.apps.googleusercontent.com'
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
        current_user = endpoints.get_current_user()
        if not current_user:
            logging.error("Yup not signed in!!!")
            raise endpoints.UnauthorizedException("Please sign in.")
        else:
            # Get couple key
            key = "Couple_Key|" + current_user.email()
            couple_key = ra_memcache.cache_entity(key,current_user.email(),None,Couple.by_email,keys_only=True)                   
            # couple_key = Couple.by_email(current_user.email(),keys_only=True)
            if not couple_key:
                # raise endpoints.UnauthorizedException("Couple key not found for %s" % current_user.email())
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

APPLICATION = endpoints.api_server([HelloWorldApi])