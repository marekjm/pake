//  ROOT should be set for each site
const ROOT = '';


function getjson(url, fallback) {
    //  url:        URL to fetch
    //  fallback:   default result in case of error
    var request = new XMLHttpRequest();
    var response = fallback;
    try {
        request.open('GET', url, false);
        request.send();
        var response = JSON.parse(request.responseText);
    }
    catch (e) {
        console.error(e);
    }
    return response;
}


var Meta = function (root) {
    this.root = root;

    this.get = function () {
        //  This will return array of mirrors.
        return getjson(this.root + '/meta.json', {});
    }
}


var Mirrors = function (root) {
    this.root = root;

    this.get = function () {
        //  This will return array of mirrors.
        return getjson(this.root + '/mirrors.json', []);
    }
}


var Packages = function (root) {
    this.root = root;

    this.get = function () {
        //  This will return array of mirrors.
        return getjson(this.root + '/packages.json', []);
    }
}


var Pake = function (root) {
    this.root = root;
    this.mirrors = new Mirrors(this.root);
    this.meta = new Meta(this.root);
    this.packages = new Packages(root);
}


var pake = new Pake(ROOT);
