/**
 * @fileoverview
 * Provides methods for the Hitlist UI and interaction with the
 * hitlist API.
 */

/** global namespace for relationshipanalytics projects. */
var ra = ra || {};

/** hitlist namespace for hitlist project. */
ra.hitlist = ra.hitlist || {};

/**
 * Client ID of the application (from the APIs Console).
 * @type {string}
 */
ra.hitlist.CLIENT_ID = '356591658043-r06nli81msv1s280plb91a2kjn25c02b.apps.googleusercontent.com';

/**
 * Scopes used by the application.
 * @type {string}
 */
ra.hitlist.SCOPES =
    'https://www.googleapis.com/auth/userinfo.email';


/**
* Whether or not the user is signed in.
* @type (boolean)
*/
ra.hitlist.signedIN = false;

/**
* Loads the application UI after the user has complted auth.
*/
ra.hitlist.userAuthed = function() {
  var request = gapi.client.oauth2.userinfo.get().execute(function(resp){
    if(!resp.code){
      ra.hitlist.signedIN = true;      
    }
  });
};

/**
 * Handles the auth flow, with the given value for immediate mode.
 * @param {boolean} mode Whether or not to use immediate mode.
 * @param {Function} callback Callback to call on completion.
 */
ra.hitlist.signin = function(mode, callback) {
  gapi.auth.authorize({client_id: ra.hitlist.CLIENT_ID,
      scope: ra.hitlist.SCOPES, immediate: mode},
      callback);
};

/**
 * Presents the user with the authorization popup.
 */
ra.hitlist.auth = function() {
  if (!ra.hitlist.signedIn) {
    ra.hitlist.signin(false,
        ra.hitlist.userAuthed);
  } else {
  	alert('you are signed in');
  }
};



/**
 * Gets a eatery's comments via the API.
 * @param {string} id ID of the eatery.
 */
ra.hitlist.getEateryNotes = function(id) {
  //alert('api executing!');
  gapi.client.hitlist.eateries.getEateryNotes({'id': id}).execute(
      function(resp) {
      	//alert(resp.code);
        if (!resp.code) {
          $('#modal-notes').html(resp.notes_comments);
          $('#myModalLabel').html(resp.restaurant_name);
          // $('#basicModal').modal('toggle');            
        }
      });
};

/**
 * Enables the button callbacks in the UI.
 */
ra.hitlist.enableButtons = function() {
  $('.notes-button').attr('disabled',false);
  var eateryID;
  var modalCaller;
  $('.notes-button').click(function(){
    //alert($(this).attr("value"));
    eateryID = $(this).attr("value");
    modalCaller = 1;
  });

  // Register table row click event.
  // $('.eatery-row').click(function () {
  //   eateryID = $(this).attr("value");
  //   modalCaller = 2;    
  // })

  $('#basicModal').on('show.bs.modal',function(e){
    // Call api
    if (modalCaller == 1){
      ra.hitlist.getEateryNotes(eateryID);  
    }    
    });
  $('#signinButton').click(ra.hitlist.auth);
  // var getGreeting = document.querySelector('#getGreeting');
  // getGreeting.addEventListener('click', function(e) {
  //   ra.hitlist.getGreeting(document.querySelector('#id').value);
  // });

};

/**
 * Initializes the application.
 * @param {string} apiRoot Root of the API's path.
 */
ra.hitlist.init = function(apiRoot) {
  // Loads the OAuth and helloworld APIs asynchronously, and triggers login
  // when they have completed.
  var apisToLoad;
  var callback = function() {
    if (--apisToLoad == 0) {
      ra.hitlist.enableButtons();
      ra.hitlist.signin(true,
          ra.hitlist.userAuthed);
    }
  }

  apisToLoad = 2; // must match number of calls to gapi.client.load()
  gapi.client.load('hitlist', 'v1', callback, apiRoot);
  gapi.client.load('oauth2', 'v2', callback);
};