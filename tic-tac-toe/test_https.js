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
fetch_url("https://www.google.com/")
//const fetch_url = await import("./test_https.js").then(mod => mod.fetch_url);