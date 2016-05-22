/**
 * System configuration for Angular 2 samples
 * Adjust as necessary for your application needs.
 */
(function (global) {
    // map tells the System loader where to look for things
    var map = {
        'app': 'lib', // 'dist'/,
        '@angular': 'node_modules/@angular',
        'angular2-in-memory-web-api': 'node_modules/angular2-in-memory-web-api',
        'rxjs': 'node_modules/rxjs',
        '@angular2-material': 'node_modules/@angular2-material',
        'moment':                     'node_modules/moment'
    };
    // packages tells the System loader how to load when no filename and/or no extension
    var packages = {
        'app': {main: 'app.js', defaultExtension: 'js'},
        'rxjs': {defaultExtension: 'js'},
        'angular2-in-memory-web-api': {defaultExtension: 'js'},
        'moment':                     { main: 'min/moment.min.js'}
    };
    var ngPackageNames = [
        'common',
        'compiler',
        'core',
        'http',
        'platform-browser',
        'platform-browser-dynamic',
        'router',
        'router-deprecated',
        'upgrade',
    ];
    // Angular Material 2 Packages to load.
    var materialPackages = [
        'core', 'toolbar', 'button', 'card', 'checkbox', 'icon', 'input', 'list', 'progress-bar',
        'progress-circle', 'radio', 'sidenav'
    ];


    // Add package entries for angular packages
    ngPackageNames.forEach(function (pkgName) {
        packages['@angular/' + pkgName] = {main: pkgName + '.umd.js', defaultExtension: 'js'};
    });

    materialPackages.forEach(function(item) {
        // All Material 2 components are prefixed with  @angular2-material and use
        // the components name as entry point.
        packages['@angular2-material/' + item] = { main: item, format: 'cjs', defaultExtension: 'js' };
    });

    var config = {
        transpiler: 'typescript',
  typescriptOptions: {
    emitDecoratorMetadata: true
  },
        map: map,
        packages: packages
    }
    System.config(config);
})(this);
