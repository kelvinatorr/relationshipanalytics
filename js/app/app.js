/**
 * Created by kdealca on 3/31/2015.
 */
(function(){
    var app = angular.module('raapp', ['ngMaterial']);

    app.run(function($log){
        $log.debug("starterApp + ngMaterial running...");
    });

})();
