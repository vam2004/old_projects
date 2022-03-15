"use strict";
var global_names_need_sanitiser = false;
var can_override_name_sanitiser = false;

const NOT_IS_A_EVENT_HANDLE = 0b00
const HANDLE_NEED_SANATISER = 0b10
const SANATISER_FROM_HANDLE = 0b01
const HANDLE_WITH_SANATISER = 0b11
function empty_function(){}
function san_allow(item){
	return item;
}

const _toString = Object.prototype.toString;

function _isString(str){
	return typeof str === "string" || _toString.call(str) === "[object String]";
}

function _isNotNullish(val){
	return val !== null && val !== undefined;
}
function _isNode(node){
	return node && node.nodeType !== undefined;
}
const _isNotInArray = (function(){
	return function(array, item){
		return Array.prototype.indexOf.apply(array, [item]) === -1
	}
})(); //PolyFill
function _isFunction(fun){
	var name = _toString.call(fun)
	return typeof fun === "function" || name === "[object Function]" || name ==="[object GeneratorFunction]" || name === "[object AsyncFunction]";
}
function san_clone_slf(slf){
	"use strict";
	return Object.seal(Object.create(null, slf && {
		names_need_sanatiser: {
			enumerable: false,
			configurable: false,
			writable: false,
			value: slf.names_need_sanatiser
		},
		id_sanatiser: {
			enumerable: false,
			configurable: false,
			writable: false,
			value: slf.id_sanatiser
		}
	}))
}

function make_id_for(id, slf){
	var func;
	if(slf && _isFunction(slf.id_sanatiser)){
		func = slf.id_sanatiser;
	} else if(global_names_need_sanitiser || (can_override_name_sanitiser && slf && slf.names_need_sanatiser)){
		func = empty_function;
	} else {
		func = san_allow;
	}
	return func(new String(id));
}

function pre_make_lib(ctn){//if not sanitiser => 1 block all, 2 allow all, other wise exception
	const lib = ctn.lib, flag = ctn.flg;
	if(_isFunction(lib)){
		var san;
		if(_isFunction(ctn.san)){
			san = ctn.san
		} else if(flag === HANDLE_WITH_SANATISER){
			san = san_allow;
		} else if(flag === HANDLE_NEED_SANATISER){
			san = empty_function;
		}
		return function(evt){
			const evt_arg = flag? [san(evt)]: []
			return function(...args){
				return lib.apply(Object.create(null), evt_arg.concat(args));
			}
		}
	}
}
function make_lib(_name_, _from_, name_sanatiser){
	if(_isFunction(name_sanatiser)){
		const name = name_sanatiser(_name_);
		if(_isNotNullish(name)){
			return pre_make_lib(_from_[name]);
		} else {
			throw new Error("Invalid Name");
		}
	} else {
		throw new Error("Cannot Sanatise");
	}
}
function define_call(slf, func){
	if(_isFunction(func)){
		slf.evt_handle = func;
	}
}
function assing_libs(slf, error_handle){
	const source = slf.pre_lib, close_libs = Object.create(null);
	const slf_san = san_clone_slf(slf);
	slf.ids_lib.forEach(name => {
		try{
			close_libs[name] = make_lib(name, source, san_allow);
		} catch(err){
			if(_isFunction(error_handle)){
				error_handle(err)
			} else {
				throw new Error("Panic!");
			}
		}
	})
	slf.evt_lib = function(evt){
		return function(lib_id){
			const name = make_id_for(lib_id, slf_san), targ = _isNotNullish(name)? close_libs[name](evt) : name;
			return _isFunction(targ)? targ : empty_function;
		}
	}
	return slf;
}

function id_isn_used(slf, name){
	return _isNotInArray(slf.ids_lib, name)
}
function cfg_ext_lib(slf, manager, id, type){
	if(_isFunction(manager)){
		const tt0 = type & 3, name = make_id_for(id, slf);
		if(_isNotNullish(name)){
			let wh = slf.pre_lib[name];
			if(id_isn_used(slf, name)){
				slf.ids_lib.push(name);
			}
			if(!_isNotNullish(wh)){
				wh = {};
			}
			if(tt0 === SANATISER_FROM_HANDLE){
				wh.san = manager;
			} else {
				wh.lib = manager;
				wh.flg = tt0;
			}
			slf.pre_lib[name] = wh;
		} else{
			throw new TypeError("Invalid Indentifier");
		}
	} else {
		throw new TypeError("Needed A Function");
	}
	return slf;
}
function build(slf, clbk, init_cache, f0, ArgThis){
	const evt_lib = slf.evt_lib, callback = clbk || slf.evt_handle;
	if(_isFunction(callback)){
		var cache = init_cache;
		return function(evt){
			const _lib = evt_lib, my_lib = _lib(evt), my_this = f0? this: ArgThis || Object.create(null);
			cache = callback.apply(my_this, [cache, my_lib]);
		}
	} else {
		throw new TypeError("Invalid Callback");
	}
}
function static_function_evt(){
	this.pre_lib = Object.create(null);
	this.ids_lib = [];
	this.evt_lib = Object.create(null);
	this.id_sanatiser = function(name){
		return name
	}
}
function make_bind(func, thisArg, flag){
	if(_isFunction(func)){
		return function(...init_args){
			var sanThis = _isNotNullish(thisArg)? thisArg: Object.create(null);
			return function(...args){
				var myThis = flag? this: sanThis;
				return func.apply(myThis, init_args.concat(args));
			}
		}
	} else {
		throw new TypeError("Expected Function");
		return empty_function;
	}
	
}
function push_this_into(func, argPos, f1, f0 = f1){
	var pos = Number(argPos) || 0;
	if(_isFunction(func)){
		return function(...args){
			const w = args[pos], myThis = f0? this: Object.create(null), p0 = pos + (!f1 | 0);
			var myArgs = args.slice(0, pos);
			myArgs[pos] = this;
			myArgs[p0] = _isNotNullish(w)? w : myArgs[p0] || undefined;
			return func.apply(myThis, myArgs.concat(args.slice(pos + 1)))
		}
	} else {
		throw new TypeError("Expected Function");
	}
}
function make_as_serial(slf, func, f0){
	if(_isFunction(func)){
		return function(...args){
			var result = func.apply(slf, args);
			return f0? result: this;
		} 
	} else {
		throw new TypeError("Expected Function");
	}
}
function make_proto(){
	static_function_evt.prototype.define_call = push_this_into(define_call);
	static_function_evt.prototype.build = push_this_into(build);
	static_function_evt.prototype.add_lib = push_this_into(cfg_ext_lib);
	static_function_evt.prototype.assing_libs = push_this_into(assing_libs);
}
function hook_evt_serial(){
	var cache = new static_function_evt();
	function hook_evt(){};
	hook_evt.prototype.build = make_as_serial(cache, push_this_into(build), true)
	hook_evt.prototype.add_lib = make_as_serial(cache, push_this_into(cfg_ext_lib))
	hook_evt.prototype.assing_libs = make_as_serial(cache, push_this_into(assing_libs))
	hook_evt.prototype.define_call = make_as_serial(cache, push_this_into(define_call))
	hook_evt.prototype.debbuger = make_as_serial(cache, push_this_into(function(...args){console.log(this, args)}))
	return hook_evt;
}
function make_test(){
	var test = (new (hook_evt_serial())).add_lib(console.log, "log", HANDLE_WITH_SANATISER).add_lib(function(evt, prop){
		return evt && evt.target && evt.target.style && evt.target.style.getPropertyValue && evt.target.style.getPropertyValue(prop);
		}, "get", HANDLE_WITH_SANATISER).add_lib(function(evt, prop, value){
		return evt && evt.target && evt.target.style && evt.target.style.getPropertyValue && evt.target.style.setProperty(prop, value);
		}, "set", HANDLE_WITH_SANATISER).add_lib(function(color){
			var result;
			if(_isString(color)){
				color = color.replaceAll(" ", "");
				if(color[0] === "#" && color.length > 6){
					result = [color.slice(1, 3), color.slice(3, 5), color.slice(5, 7)].map(function(i){return parseInt(i, 16)});
				} else if(color.match("rgb\\(")){
					result = color.replace("rgb(", "").replace(")", "").split(",").map(parseInt)
				}
				return result;
			}
		}, "parseColor", NOT_IS_A_EVENT_HANDLE).add_lib(function(colorArray){
			return colorArray.map(function(i, j){return (i & 255) * (1 << j)}).reduce(function(a, b){return a + b}) & 0xFFFFFF
		}, "parseColorArray", NOT_IS_A_EVENT_HANDLE).add_lib(function(color){
			var result;
			if(Array.isArray(color)){
				return "rgb(".concat(color.join(","), ")")
			} else if(typeof color === "number"){
				return "#".concat(color.toString(16)).padEnd(7, 0);
			}
		}, "makeColor", NOT_IS_A_EVENT_HANDLE).define_call(function(cache, lib){
			var t0 = lib("parseColor")(cache), t1 = (t0 ||  [0, 0, 0]), t2 = lib("parseColorArray")(t1), t3 = (t2  + 0x070605) & 0xFFFFFF, t4 = lib("makeColor")(t3);
			lib("set")("background-color", t4)
			return t4;
	}).assing_libs(console.log);
	return function(mtest){
		document.querySelector("div.div-sample").addEventListener("click", test.build(mtest, "#705060"));
	}
}
