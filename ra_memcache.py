import models
import logging

from google.appengine.api import memcache

# Memcache functions.
def hitlist_cache(key,couple_key,update=False):
    # Try to get list on Eatery entity keys from memcache
    hitlist = memcache.get(key)
    if not hitlist or update:        
        # Query all Eatery entities whose ancestor is the user's Couple
        hitlist_query = models.Eatery.all(keys_only=True).ancestor(couple_key)
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
