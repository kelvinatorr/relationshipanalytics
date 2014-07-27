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
* Add's a Google map marker on the given latitude and longitude and centers the map on it too.
* @param {float} latitude
* @param {float} longitude
*/
ra.hitlist.edit.markAndCenterMap = function(latitude,longitude){
	// Add marker to the displayed google map.	    
	var n = document.createElement("google-map-marker");
	n.setAttribute('latitude',latitude);
	n.setAttribute('longitude',longitude);
	var gmap = document.querySelector('google-map');
	// Remove previous marker.
	while (gmap.firstChild) {
    	gmap.removeChild(gmap.firstChild);
	}
	// Add new marker.
	gmap.appendChild(n);
	// Move the focus of the map to the marker.
	gmap.setAttribute('latitude',latitude);
	gmap.setAttribute('longitude',longitude);
};

/**
* Add a button to the coordinates label that allows the user to access the geocoding service.
*/
ra.hitlist.edit.addGeocodeLink = function(){
	// Change label of coordinates to include geocoding button
    var b = document.createElement("a");
    b.setAttribute('href',"javascript:void(0);");
    b.setAttribute('id','geocodeButton');
    b.setAttribute('data-toggle','tooltip')
    b.setAttribute('title','Get the latitude and longitude for the given address')
    b.innerHTML = "Geocode";
    var coordinatesLabel = document.getElementById('coordinatesLabel');
    coordinatesLabel.innerHTML = "";      	 	
    // Add click event listener to the button.      	 	
	b.addEventListener("click", hitlistGeocodeInit, false);
	coordinatesLabel.appendChild(b);
 	$('#geocodeButton').tooltip();
};

/**
* Remove the button on the coordinates label that allows the user to access the geocoding service.
*/
ra.hitlist.edit.removeGeocodeLink = function(){
	var coordinatesLabel = document.getElementById('coordinatesLabel');
	var geocodeButton = document.getElementById('geocodeButton');
	coordinatesLabel.removeChild(geocodeButton);
	coordinatesLabel.innerHTML = "Coordinates";
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
	    // Mark and center map.
	    ra.hitlist.edit.markAndCenterMap(locationResult.lat(),locationResult.lng());
	    // Change the value of the geocode input box.
	    document.getElementById('coordinates').value = locationResult.lat() + "," + locationResult.lng();
	    // Call the function that saves the coordinates to the DB.
	    ra.hitlist.edit.saveGeocode(locationResult.lat(),locationResult.lng());
	    // Change label of coordinates input box.
	    ra.hitlist.edit.removeGeocodeLink();
	  }
	  else{	    
	    document.getElementById('geocode-error').innerHTML = "Geocode unsuccessful: " + status;
	  }        
	});
};