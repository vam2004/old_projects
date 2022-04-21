class locked_request {
	constructor(action, data){
		this.data = data
		this.action = action
	}
}
class unkown_action extends Error {
	constructor () {
		super("Unkown Action When Requesting");
	}
}
class game_server{
	constructor(config) {
		this.config
		this.stormlock = Map(Object.entries({
			"pause": false,
			"subimit": false,
			"update": false,
			"exit": false,
			"join": false
		}))
		
	}
	get_lock(action, time) {
		const self = this;
		if (this.stormlock.get(action)) {
			return false;
		} else {
			if (this.stormlock.has(action)) {
				this.stormlock.set(action, true);
				window.setTimeout(function(){
					self.release_lock(action);
				}, time);
				return true;
			} else {
				throw unkown_action()
			}
			
		}
	}
	release_lock(action) {
		this.stormlock[action] = false;
	}
	raw_request(src) {
		const address = this.config.server_address
		const init = {
		method: "POST", 
		body: JSON.stringify(src), 
		mode: "cors", 
		Headers: {"Content-Type":"text/plain"}}
		return fetch(address, init).then(data => data.json())
	}
	request_action(action, data, unlocked, lock_time) {
		if (unlocked || this.get_lock(action, lock_time)) {
			return this.raw_request({action: data})
		} else {
			throw new locked_request(action, data);
		}
	}
	request_pause() {
		this.request_action("pause")
	}
}

function create_ws(onopen, onclose) {
	const no_fn = function () {};
	const ws = new WebSocket("ws://" + window.location.host);
	ws.addEventListener('open', onopen || no_fn);
	ws.addEventListener('close', onclose || no_fn);
	const as_promise = new Promise(function (res, err) {
		ws.addEventListener('message', res);
		ws.addEventListener('error', err);
	});
	return {ws, then: function(callback) {
		callback()
	}}
}
