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
 * @type {int64}
 */
ra.hitlist.edit.EATERYID;

/**
* Uses Google's geocoding api to convert the eatery's address into coordinates.
* @param {float} latitude
* @param {float} longitude
*/
ra.hitlist.edit.saveGeocode = function(latitude,longitude){
	//Build the Request Object
	var requestData = {};
	requestData.latitude = latitude;
	requestData.longitude = longitude;
	requestData.eatery_id = ra.hitlist.edit.EATERYID;
	gapi.client.hitlist.eateries.geocode(requestData).execute(function(resp) {
		// Inform user that the coordinates have been saved to the database.
	  	var geocodeError = document.getElementById('geocode-error');
	  	geocodeError.innerHTML = "Coordinates have been saved to the database."
	  	geocodeError.classList.toggle('errorMessage',false);
	  	geocodeError.classList.toggle('dbMessage',true);
	});
};

/**
* Uses Google's geocoding api to convert the eatery's address into coordinates.
* @param {string} A complete address string assembled from the input elements.
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
	    ra.hitlist.edit.saveGeocode(locationResult.lat(),locationResult.lng());
	    // Change label of coordinates input box.
	    var coordinatesLabel = document.getElementById('coordinatesLabel');
	    var geocodeButton = document.getElementById('geocodeButton');
	    coordinatesLabel.removeChild(geocodeButton);
	    coordinatesLabel.innerHTML = "Coordinates";

	  }
	  else{	    
	    document.getElementById('geocode-error').innerHTML = "Geocode unsuccessful: " + status;
	  }        
	});
};