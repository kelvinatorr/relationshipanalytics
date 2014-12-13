#!/usr/bin/python

"""ProtoRPC message class definitions for RelationshipAnalytics Hitlist API."""
from protorpc import message_types
from protorpc import messages


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