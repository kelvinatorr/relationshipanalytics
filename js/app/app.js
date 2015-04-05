/**
 * Created by kdealca on 3/31/2015.
 */
(function(){
    var app = angular.module('raApp', ['ngMaterial']);

    app.config(['$mdThemingProvider', '$mdIconProvider', function($mdThemingProvider, $mdIconProvider){

        $mdIconProvider
            .defaultIconSet("static/svg/avatars.svg", 128)
            .icon("menu"       , "static/svg/menu.svg"        , 24);
            //.icon("share"      , "./assets/svg/share.svg"       , 24)
            //.icon("google_plus", "./assets/svg/google_plus.svg" , 512)
            //.icon("hangouts"   , "./assets/svg/hangouts.svg"    , 512)
            //.icon("twitter"    , "./assets/svg/twitter.svg"     , 512)
            //.icon("phone"      , "./assets/svg/phone.svg"       , 512);

        $mdThemingProvider.theme('default')
            .primaryPalette('brown')
            .accentPalette('red');

    }]);

    app.run(['$log',function($log){
        $log.debug("starterApp + ngMaterial running kelvin...");
    }]);

    var RandomController = function($mdSidenav, $mdBottomSheet, $log, $q) {

        var self = this;

        /**
         * First hide the bottomsheet IF visible, then
         * hide or Show the 'left' sideNav area
         */
        self.toggleSideMenu = function() {
            var pending = $mdBottomSheet.hide() || $q.when(true);

            pending.then(function(){
                $mdSidenav('leftSideNav').toggle();
            });
        };

        //var okToGreet = false;
        //
        //var promise = new Promise(function(resolve, reject) {
        //    // do a thing, possibly async, then…
        //
        //    if (okToGreet) {
        //        resolve("Stuff worked!");
        //    }
        //    else {
        //        reject(Error("It broke"));
        //    }
        //});
        //
        //promise.then(function(message){
        //    alert(message);
        //}, function(message){
        //    alert(message);
        //});

    };

    app.controller("RandomController", [
        '$mdSidenav', '$mdBottomSheet', '$log','$q',
        RandomController
    ]);



})();
