import sqlite3 from "sqlite3";
import path from "path";
export function create_db(user_dir, session_dir) {
	const user_db = new sqlite3.Database(user_dir);
	const session_db = new sqlite3.Database(session_dir);
	user_db .serialize(function(){
		user_db.exec("CREATE TABLE IF NOT EXISTS social_auth (id INTEGER PRIMARY KEY, hash BLOB, tries INTEGER, expires INTEGER);");
		user_db.exec("CREATE TABLE IF NOT EXISTS users_auth (hash_name BLOB PRIMARY KEY, hash_pass BLOB, tries INTEGER, until INTEGER, pass_expires INTEGER, session_expires INTEGER, token_id INTEGER, FOREIGN KEY(token_id) REFERENCES social_auth(id));");
		/*
			'hash_name' is the user's hashed name ,
			'hash_pass' is the user's hashed password,
			'tries' is the amount of tries of user's autentication,
			'until' is the user's actual passord expiration date,
			'default_expires' is the default expiration date when users connect,
			'token_id' is the foreign key for the tokens to autenticate request beetween user
		(to broadcast when the user connect).
		*/
	});
	session_db.run("CREATE TABLE IF NOT EXISTS sessions (user_id INTEGER PRIMARY KEY, until INTEGER, FOREIGN KEY(user_id) REFERENCES users_auth(__rowid__));");
	return {user_db, session_db};
};
export function open_db(dir) {
	const db = new sqlite3.cached.Database(dir);
	return db;
};
export const db_debug {
	exec: function(...args){
		console.log(...args);
	}
}
function must_int(src, nullish, msg) {
	if (pass_null && (src == undefined || src == null)) {
		return null;
	} else {
		let tmp = int(src);
		if(!isFinite(src)) throw Error(msg);
		return tmp;
	}
}
function create_manager() {
	function manage_db(db, config){
		this.db = db;
		this.config = config;
	};
	manage_db.prototype.close = function(){
		this.db.close();
	};
	manage_db.prototype.add_user = function(hash_name, hash_pass, expires, session_expires, token_id){
		const db = this.db;
		const now = int(Date.UTC() / 1000);
		expires = must_int(expires, false, "Invalid Password Expiration");
		token_id = must_int(token_id, true, "Invalid Broadcast Id");
		session_expires = must_int(session_expires, false, "Invalid Session Expiration");
		db.exec("INSERT INTO users_auth VALUES ($name, $pass, 0, $e, $de, $se, $i)", {
			$name: hash_name,
			$pass: hash_pass,
			$e: expires && (expires + now),
			$de: expires,
			$se: session_expires,
			$i: token_id
		});
	}
}
function create_session(user_id, )