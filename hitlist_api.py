import endpoints
import logging
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from time import sleep

import ra_memcache
# Import api messages
from hitlist_api_messages import EateryNotes
from hitlist_api_messages import EateryLocation
from hitlist_api_messages import EateryLocationCollection

from models import Eatery
from models import Couple

WEB_CLIENT_ID = '356591658043-r06nli81msv1s280plb91a2kjn25c02b.apps.googleusercontent.com'
ANDROID_CLIENT_ID = 'replace this with your Android client ID'
IOS_CLIENT_ID = 'replace this with your iOS client ID'
ANDROID_AUDIENCE = WEB_CLIENT_ID
package = 'hitlist'


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
        geocoded_hitlist_key = "GeocodedHitlist|" + str(couple_key.key().id())
        # Get a list of Entity keys that are associated with this user and have been geocoded.        
        geocoded_hitlist = ra_memcache.geocoded_hitlist_cache(geocoded_hitlist_key,couple_key)
        # List of response messages.
        items = []
        for e in geocoded_hitlist:
            # Initialize the EateryMessage            
            e_message = EateryLocation(restaurant_name=e.RestaurantName,latitude=e.Latitude,longitude=e.Longitude,geocoded=True,status_code=status_code)
            items.append(e_message)
        return EateryLocationCollection(items=items)

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
            geocoded_hitlist_key = "GeocodedHitlist|" + str(couple_key.key().id())            
            geocoded_hitlist = ra_memcache.geocoded_hitlist_cache(geocoded_hitlist_key,couple_key,update=True)
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