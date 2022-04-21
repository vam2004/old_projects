/*
The base of source code has found on a topic on the network, but it will be userful for ad-hoc testing when it is ready for migrating to https
*/

import https from "https";
export function fetch_url(url) {
	return new Promise(function(res, rej) {
		const req = https.get(url, function(sucess) {
			sucess.on("data", function(data) {
				//do something
			});
			sucess.on("end", function() {
				console.log("sucess: [" + url + "]")
			});
		});
		req.on("error", function(error) {
			rej(error);
		});
	});
}
fetch_url("https://developer.mozilla.org")
fetch_url("https://nodejs.org/en/")

//const fetch_url = await import("./test_https.js").then(mod => mod.fetch_url);
