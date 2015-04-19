/**
 * Created by kdealca on 3/31/2015.
 */
(function(){
    var app = angular.module('raApp', ['ngMaterial']);

    app.config(['$mdThemingProvider', '$mdIconProvider', function($mdThemingProvider, $mdIconProvider){

        $mdIconProvider
            .defaultIconSet("static/svg/svg-sprite-maps.svg", 128)
            .icon("menu", "static/svg/menu.svg", 24)
            //.iconSet("glyphicons", "fonts/glyphicons-halflings-regular.svg", 24);
            .icon("call", "static/svg/ic_call_24px.svg", 24)
            .iconSet('action', 'static/svg/action-icons.svg', 24)
            .iconSet('alert', 'static/svg/alert-icons.svg', 24)
            .iconSet('av', 'static/svg/av-icons.svg', 24)
            .iconSet('communication', 'static/svg/communication-icons.svg', 24)
            .iconSet('content', 'static/svg/content-icons.svg', 24)
            .iconSet('device', 'static/svg/device-icons.svg', 24)
            .iconSet('editor', 'static/svg/editor-icons.svg', 24)
            .iconSet('file', 'static/svg/file-icons.svg', 24)
            .iconSet('hardware', 'static/svg/hardware-icons.svg', 24)
            .iconSet('icons', 'static/svg/icons-icons.svg', 24)
            .iconSet('image', 'static/svg/image-icons.svg', 24)
            .iconSet('maps', 'static/svg/maps-icons.svg', 24)
            .iconSet('navigation', 'static/svg/navigation-icons.svg', 24)
            .iconSet('notification', 'static/svg/notification-icons.svg', 24)
            .iconSet('social', 'static/svg/social-icons.svg', 24)
            .iconSet('toggle', 'static/svg/toggle-icons.svg', 24);

        $mdThemingProvider.theme('default')
            .primaryPalette('brown')
            .accentPalette('red');

    }]);

    app.run(['$log',function($log){
        $log.debug("starterApp + ngMaterial running kelvins...");
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
