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

ra.hitlist.map.initialize = function(){
  geocoder = new google.maps.Geocoder();
  // Get current location.
  ra.hitlist.map.geoLocateUser();
  //ra.hitlist.map.addMapMarkers();
};
	
