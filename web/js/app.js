var app = angular.module('wateringApp', ['ngMaterial', 'ngMessages', 'material.svgAssetsCache']);

app.config(function ($mdThemingProvider) {
    $mdThemingProvider.theme('default')
        .primaryPalette('blue')
        .accentPalette('red');
});

app.filter("momentFromNow", function () {
    return function (input) {
        console.log(input + "Z");
        return moment(input + "Z").fromNow();
    }
});

app.controller('WateringController', function ($http, $scope, $rootScope, $location, $mdDialog, $mdMedia) {
    
    var self = this;

    $rootScope.rx = self;

    self.count = 0;
    self.local_status = "initialized";
    self.remote_status = "none";
    self.error = "";
    self.mode = "none";
    self.isError = false;

    self.isWatering = false;

    self.baseurl = "/watering.api/";

    self.waterFor = function (duration) {
        self.isWatering = true;

        $http.get(self.baseurl + "water/" + duration)
            .then(function successCallback(response) {
                self.error = response.data;
                self.isError = false;
                self.isWatering = false;
                self.getHistory();
            }, function errorCallback(response) {
                self.error = response;
                self.isError = true;
                self.isWatering = false;
            });
    };

    self.recordRefill = function (event) {
        //var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
        $mdDialog.show({
            controller: DialogController,
            templateUrl: 'refill.dialog.html',
            parent: angular.element(document.body),
            targetEvent: event,
            clickOutsideToClose: true,
            fullscreen: false
        })
            .then(function (answer) {
                $scope.status = 'You said the information was "' + answer + '".';
            }, function () {
                $scope.status = 'You cancelled the dialog.';
            });
        /*$scope.$watch(function() {
          return $mdMedia('xs') || $mdMedia('sm');
        }, function(wantsFullScreen) {
          $scope.customFullscreen = (wantsFullScreen === true);
        });*/
    };

    self.getHistory = function () {
        $http.get(self.baseurl + "history")
            .then(function successCallback(response) {
                self.history = response.data;
            }, function errorCallback(response) {
                self.error = response;
            });
    };

    self.refill = function (volume) {
        $http.get(self.baseurl + "refill/" + volume)
            .then(function successCallback(response) {
                self.getHistory();
            }, function errorCallback(response) {
                self.error = response;
            });

    };

    self.getHistory();
});

function DialogController($scope, $mdDialog, $rootScope) {
    self = this;
    $scope.hide = function () {
        $mdDialog.hide();
    };
    $scope.cancel = function () {
        $mdDialog.cancel();
    };
    $scope.save = function () {
        $rootScope.rx.refill($scope.bag.refillVolume);

        $mdDialog.hide();
    };
    $scope.bag = {
        refillVolume: null
    };
}