/**
 * Created by kdealca on 3/31/2015.
 */
(function(){
    var app = angular.module('raApp', ['ngMaterial']);

    app.config(['$mdThemingProvider', '$mdIconProvider','$interpolateProvider',
        function($mdThemingProvider, $mdIconProvider, $interpolateProvider){

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
                .primaryPalette('light-blue')
                .accentPalette('pink');

            $interpolateProvider.startSymbol('||');
            $interpolateProvider.endSymbol('||');
        }
    ]);



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

        self.options = [];

        var optionCount = 0;

        /**
         * Helper function that generates a newOption Model
         * @returns {{id: number, description: string}}
         */
        var generateNewOption = function() {
            optionCount += 1;
            return {
                id: optionCount,
                description: ''
            };
        };

        /**
         * Bound to the input box, represents new options for users to enter
         * @type {{id: number, description: string}}
         */
        self.newOption  = generateNewOption();

        /**
         * Bound to the add button, adds the option that the user typed in to the array
         *
         */
        self.add = function(){
            if (self.newOption.description === '') return;
            // Add to array.
            self.options.push(self.newOption);
            self.newOption = generateNewOption();
        };

        /**
         * Bound o the trash can icon, delete an option from the array.
         * @param id
         */
        self.delete = function(id) {
            var idx = self.options.map(function(e){return e.id}).indexOf(id);
            self.options.splice(idx,1);
        };

        /**
         * True if the pick button has been pressed.
         * @type {boolean}
         */
        self.hasNotPicked = true;

        /**
         * The number of times the pick button has been pressed.
         * @type {number}
         */
        self.pickCount = 0;

        /**
         * The option that was randomly picked.
         */
        self.pick;

        /**
         * Bound to the pick button, selects an option from the options array randomly
         */
        self.pickRandom = function() {
            self.pick = self.options[Math.floor(Math.random() * self.options.length)];
            if(self.hasNotPicked) self.hasNotPicked = false;
            self.pickCount += 1;
        };

        /**
         * Resets the app state to pristine, no options, no picks.
         */
        self.reset = function() {
            self.options = [];
            optionCount = 0;
            self.newOption  = generateNewOption();
            self.pick = undefined;
            self.hasNotPicked = true;
            self.pickCount = 0;
        }


    };

    app.controller("RandomController", [
        '$mdSidenav', '$mdBottomSheet', '$log','$q',
        RandomController
    ]);



})();
