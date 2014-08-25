/**
 * @fileoverview
 * Provides methods for authenticating a relationship analytics user.
 */

/** global namespace for relationshipanalytics projects. */
var ra = ra || {};

/** auth namespace for relationship analytics. */
ra.auth = ra.auth || {};

/**
 * Client ID of the application (from the APIs Console).
 * @type {string}
 */
ra.auth.CLIENT_ID =
    '706028337645-oe249o4vs0lsm199561e6pdua98vk9ge.apps.googleusercontent.com';

/**
 * Scopes used by the application.
 * @type {string}
 */
ra.auth.SCOPES =
    'https://www.googleapis.com/auth/userinfo.email';

/**
* Whether or not the user is signed in.
* @type (boolean)
*/
ra.auth.signedIN = false;


/**
 * Handles the auth flow, with the given value for immediate mode.
 * @param {boolean} mode Whether or not to use immediate mode.
 * @param {Function} callback Callback to call on completion.
 */
ra.auth.signin = function(mode, callback) {
  gapi.auth.authorize({client_id: ra.auth.CLIENT_ID,
      scope: ra.auth.SCOPES, immediate: mode},
      function(){
        var request = gapi.client.oauth2.userinfo.get().execute(function(resp){
          if(!resp.code){
            ra.auth.signedIN = true;
            console.log("userAuthed is done.");
            if (callback != undefined) {
              callback();
            }
          }
        });
      });
};

/**
 * Initializes the application.
 * @param {string} apiRoot Root of the API's path.
 */
ra.auth.init = function(apiRoot,pageCallback) {
  // Loads the OAuth and helloworld APIs asynchronously, and triggers login
  // when they have completed.
  var apisToLoad;
  var callback = function() {
    if (--apisToLoad == 0) {      
      ra.auth.signin(true,
          pageCallback);      
    }
  }

  apisToLoad = 2; // must match number of calls to gapi.client.load()
  gapi.client.load('hitlist', 'v1', callback, apiRoot);
  gapi.client.load('oauth2', 'v2', callback);
};