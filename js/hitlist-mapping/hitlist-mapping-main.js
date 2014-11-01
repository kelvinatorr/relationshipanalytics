/**
 * @fileoverview
 * Provides methods for the map feature of the hitlist project.
 */

/** global namespace for relationshipanalytics projects. */
var ra = ra || {};

/** hitlist namespace for hitlist project. */
ra.hitlist = ra.hitlist || {};

/** hitlist namespace for hitlist editing. */
ra.hitlist.map = ra.hitlist.map || {};

/**
 * User's last detected location.
 * @type {latitude:,longitude:}
 */
ra.hitlist.map.CURRENT_LOCATION = {};

/**
 * Handler for geolocation failure 
 */
ra.hitlist.map.geoLocateUserError = function(){
	alert('Unable to retrieve your location');
};

/**
 * Handler for geolocation success.
 * @param{Object}
 */
ra.hitlist.map.geoLocateUserSuccess = function(position){      
	// Change google-map element latitude and longitude attributes.
	var gmap = document.querySelector('google-map');
	gmap.setAttribute('latitude',position.coords.latitude);
	gmap.setAttribute('longitude',position.coords.longitude);
    // Set the current location global variable.
    ra.hitlist.map.CURRENT_LOCATION.latitude = position.coords.latitude;
    ra.hitlist.map.CURRENT_LOCATION.longitude = position.coords.longitude;
    var n = document.createElement("google-map-marker");
    n.setAttribute('latitude',position.coords.latitude);
    n.setAttribute('longitude',position.coords.longitude);
    document.querySelector('google-map').appendChild(n);
};

/**
 * Use the browsers geolocation api to get the user's current location.
 */
ra.hitlist.map.geoLocateUser = function(){
  var geoOptions = {
    enableHighAccuracy: true
    ,maximumAge: 60000     
  };

  if ("geolocation" in navigator) {
    /* geolocation is available */
    navigator.geolocation.getCurrentPosition(ra.hitlist.map.geoLocateUserSuccess,ra.hitlist.map.geoLocateUserError,geoOptions);
  } else {
    /* geolocation IS NOT available */
    alert("Geolocation is not available.");
  }
};

/**
 * Calculate the distance in kilometers between 2 geographic points.
 * @param {number} Latitude of point1
 * @param {number} Longitude of point1
 * @param {number} Latitude of point2
 * @param {number} Longitude of point2
 * @return {number} Distance in km between the 2 coordinates.
 */
ra.hitlist.map.calcDistance = function(lat1, lon1, lat2, lon2) {
    var R = 6371;
    var a =
        0.5 - Math.cos((lat2 - lat1) * Math.PI / 180) / 2 +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        (1 - Math.cos((lon2 - lon1) * Math.PI / 180)) / 2;
    return R * 2 * Math.asin(Math.sqrt(a));
};

/**
 * Find the 10 closest points from a users location.
 * @param {Array.object} List of hitlist locations
 * @return {Array.object} List of 10 closest points
 */
ra.hitlist.map.findClosestPoints = function(hitlistLocations) {
    for (var i = 0; i < hitlistLocations.length; i++) {
        var e = hitlistLocations[i];
        var d2 = ra.hitlist.map.calcDistance(ra.hitlist.map.CURRENT_LOCATION.latitude, ra.hitlist.map.CURRENT_LOCATION.longitude, e.latitude, e.longitude);
        e.distance = d2;
        //alert(d2);
    }
    // Sort result list ascending.
    hitlistLocations.sort(function(a, b) {
        return a.distance - b.distance;
    });
    // Return the top 10 closest.
    return hitlistLocations.slice(0, 10);
};

/**
 * Add hitlist location markers to the google-map element
 */
ra.hitlist.map.addMapMarkers = function() {
    // Run api calling function.    
    gapi.client.hitlist.eateries.getLocations().execute(function(resp) {
    	var hitlistLocations = resp.items;        
        // Filter for the 10 closest points.
        var tenClosest = ra.hitlist.map.findClosestPoints(hitlistLocations);        
        // Add the 10 closest to the map as markers
        for (var i = 0; i < tenClosest.length;i++){
            var n = document.createElement("google-map-marker");
            n.setAttribute('latitude',tenClosest[i].latitude);
            n.setAttribute('longitude',tenClosest[i].longitude);
            // Set the title of the marker
            n.setAttribute('title', 'Hi Kelvin');
            // Set a h3 tag as a child of the marker so it shows up when they click on it.
            document.querySelector('google-map').appendChild(n);
        }
    });    
};

ra.hitlist.map.initialize = function(){
  geocoder = new google.maps.Geocoder();
  // Get current location.
  ra.hitlist.map.geoLocateUser();  
  ra.hitlist.map.addMapMarkers();
};
	
