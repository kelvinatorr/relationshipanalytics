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
	geocoder.geocode( { 'address': addressString}, function(results, status) {
	  if(status == google.maps.GeocoderStatus.OK){   
	    var locationResult = results[0]['geometry']['location'];	    
	    var n = document.createElement("google-map-marker");
	    n.setAttribute('latitude',locationResult.lat());
	    n.setAttribute('longitude',locationResult.lng());
	    document.querySelector('google-map').appendChild(n);
	  }
	  else{
	    alert("Geocode unsuccessful: " + status);
	  }        
	});
};