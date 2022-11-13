const fs = require('fs');
const { exit } = require('process');

var package_json = require('./package.json'); //(with path)
var version_json = require("./version.json")
package_json.version = version_json.version


fs.writeFile("./package.json", JSON.stringify(package_json, null, 4), err => {
    if (err) {
        console.log("Error while updating version");
        throw err;
    }
    console.log("Updated package.json succesfully to " + version_json.version + "(" + package_json.version + ")");
    exit(0)
});