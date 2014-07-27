/**
 * @fileoverview
 * Provides methods for the Hitlist UI and interaction with the
 * hitlist API.
 */

/** global namespace for relationshipanalytics projects. */
var ra = ra || {};

/** hitlist namespace for hitlist project. */
ra.hitlist = ra.hitlist || {};


/** hitlist namespace for hitlist editing. */
ra.hitlist.edit = ra.hitlist.edit || {};

/**
 * The EateryID of the currently viewed eatery
 * @type {latitude:,longitude:}
 */
ra.hitlist.edit.EATERYID;

/**
* Uses Google's geocoding api to convert the eatery's address into coordinates.
*/
ra.hitlist.edit.googleGeocode = function(addressString) {
	geocoder = new google.maps.Geocoder();
	geocoder.geocode( { 'address': addressString}, function(results, status) {
	  if(status == google.maps.GeocoderStatus.OK){   
	    var locationResult = results[0]['geometry']['location'];
	    // Add marker to the displayed google map.	    
	    var n = document.createElement("google-map-marker");
	    n.setAttribute('latitude',locationResult.lat());
	    n.setAttribute('longitude',locationResult.lng());
	    var gmap = document.querySelector('google-map');
	    gmap.appendChild(n);
	    // Move the focus of the map to the marker.
	    gmap.setAttribute('latitude',locationResult.lat());
	    gmap.setAttribute('longitude',locationResult.lng());
	    // Change the value of the geocode input box.
	    document.getElementById('coordinates').value = locationResult.lat() + "," + locationResult.lng();
	    // Call the function that saves the coordinates to the DB.
	  }
	  else{	    
	    document.getElementById('geocode-error').innerHTML = "Geocode unsuccessful: " + status;
	  }        
	});
};