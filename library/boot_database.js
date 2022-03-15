"use strict";
const OPTION_1_ONLY_ = 0b01;
const OPTION_2_ONLY_ = 0b10;
const _OPTION_EVERY_ = 0b11;
const _WHEN_AFTER_TM = OPTION_1_ONLY_;
const _WHEN_BEFORE_T = OPTION_2_ONLY_; 
const _WHEN_BOTH_TM_ = _OPTION_EVERY_;
const QUERY_DATA_ONL = OPTION_1_ONLY_;
const QUERY_ERR_ONLY = OPTION_2_ONLY_;
const QUERY_BOTH_FLG = _OPTION_EVERY_;
const ERR_N_IS_FUNC_ = "Not is Function";
const ERR_GEN_INV_OP = "Failed to Parse"; 
const ERR_INV_TIMER_ = "Dangeous Timer!";
const ERR_ISN_CLOSED = "Not Encapsulate"; 
const ERR_BY_CLEANED = "Broken waitlist";
const TIMER_SINGLE_M =  1;
const TIMER_ALWAYS_M =  0;
const TIMER_HAS_TIME = true;
const TIMER_NOT_TIME = false;
const QUERY_ERR_TYPE = true;
const QUERY_DAT_TYPE = false;
const QUERY_AFTER_N_ = 1;
const QUERY_BEFORE_N = 0;
const SAFE_THIS_SET_ = null;

class _general_error_ extends Error{//ERROR_GENERIC
	#error_at;
	constructor(message, _object){
		super(message);
		this.#error_at = _object;
	}
	get error_at(){
		return this.#error_at;
	}
}
class _invalid_option extends _general_error_{//ERROR_UNKOWN_OPTION
	constructor(_object){
		super(ERR_GEN_INV_OP, _object)
	}
}
class _invalid_timer_ extends _general_error_{//ERROR_UNKOWN_TIMER
	constructor(_object){
		super(ERR_INV_TIMER_, _object)
	}
}
class _no_closed_func extends _general_error_{//ERROR_UNKOWN_CALLBACK
	constructor(_object){
		super(ERR_ISN_CLOSED, _object);
	}
}
class not_is_function extends _general_error_{//ERROR_UNKOWN_FUNCTION
	constructor(_object){
		super(ERR_N_IS_FUNC_, _object);
	}
}
class clean_waitlist_ extends Error{//ERROR_CLEANED_DATABASE
	constructor(){
		super(ERR_BY_CLEANED);
	}
}
function check_val_func_(func){//CHECK_FUNCTION
	return typeof func === "function";
}
function clean_sync_call(_callback_, ...args){//SANITISE_CALLBACK
	try{
		if(check_val_func_(_callback_)){
			_callback_(...args);
		} else {
			throw new not_is_function();
		}
	} catch(_err) {
		console.log(_err);	
	}	
}
function clean_callback_(_callback_, ...args){//SANITISE_CALLBACK_WITH_ASYNC
	setTimeout(clean_sync_call, 0, _callback_, ...args);
}
function _cut_the_bit_at(token, where){
	return (token & (1 << where)) >> where
}
function _generic_parse_(token, _err, flag){//PARSE_OPTION
	let b_set = [token & 1, (token & 2) >> 1];
	if(!b_set[0] && !b_set[1] && (flag || _err)){
		let _bug = new _invalid_option(ERR_GEN_INV_OP);
		if(flag){
			throw _bug;
		} else {
			clean_sync_call(_err, _bug);
		} 
	}
	return b_set;
}
function check_if_nullish_(source){
	return !(source ^ (source ?? true));
}
function check_valid_timer(timer){
	return timer instanceof lookup_hash_timer;
}
class lookup_closed_fun{//CLOSED_CALLBAK
	#timer; #_func;
	constructor(_func, timer){
		if(!check_valid_timer(timer)){
			throw new _invalid_timer_(timer);
		} else if(check_val_func_(_func)){
			this.#timer = timer;
			this.#_func = _func;
		} else {
			throw new _no_closed_func(_func);
		}
	}
	clone(timer = this.#timer, _func = this.#_func){
		return new this.constructor(_func, timer);
	}
	get timer(){
		return this.#timer;
	}
	get _func(){
		return this.#_func;
	}
}
function check_closed_func(func){
	return func instanceof lookup_closed_fun;
}
function _garbage_closed_f(cont){
	let timer = check_closed_func(cont) && check_val_func_(cont._func) && check_valid_timer(cont.timer) && cont.timer;
	return !!(timer && (timer.exec || timer.keep));
}
class lookup_hash_timer{
	#time; #exec; #keep;
	constructor(time){
		this.#time = time;
		this.#exec = true;
		this.#keep = true;
	}
	count(){
		let time = this.#time
		let keep;
		this.#exec = this.#keep;
		if(time > TIMER_SINGLE_M) {
			this.#time = time - 1;
			this.#keep = TIMER_HAS_TIME;
		} else if(time === TIMER_SINGLE_M) {
			this.#keep = TIMER_NOT_TIME;
		} else {
			this.#keep = TIMER_HAS_TIME;
		}
		return this;
	}
	get time(){
		return this.#time;
	}
	get exec(){
		return this.#exec;
	}
	get keep(){
		return this.#keep;
	}
}
function make_encapsulated(func, time = TIMER_SINGLE_M){
	return new lookup_closed_fun(func, new lookup_hash_timer(time));
}
function keep_context_func(func, ...args){
	if(check_val_func_(func)){
		return Function.prototype.call.bind(func, SAFE_THIS_SET_, ...args);
		
	} else {
		throw new not_is_function(func);
	}
}
class _entry_hash_table{
	#listen_data; #listen_err_; #kstore_data; #kstore_err_; #keep_data_n; #keep_error_; #count_data_; #count_error;
	constructor(keep_data_ = 1, keep_error = 1){
		this.#listen_data = new Array();
		this.#listen_err_ = new Array();
		this.#kstore_data = new Array();
		this.#kstore_err_ = new Array();
		this.#keep_data_n = keep_data_;
		this.#keep_error_ = keep_error;
		this.#count_data_ = 0;
		this.#count_error = 0;
	}
	#select_type(type){
		let quere, where, count, times;
		if(type){
			quere = Array.from(this.#listen_err_);
			where = Array.from(this.#kstore_err_);
			count = this.#keep_error_;
			times = this.#count_error;
		} else {
			quere = Array.from(this.#listen_data);
			where = Array.from(this.#kstore_data);
			count = this.#keep_data_n;
			times = this.#count_data_;
		}
		return {quere, where, count, times};
	}
	#assign_t(type, quere, where, times){
		if(type){
			this.#listen_err_ = quere ?? this.#listen_err_;
			this.#kstore_err_ = where ?? this.#kstore_err_;
			this.#count_error = times ?? this.#count_error;
		} else {
			this.#listen_data = quere ?? this.#listen_data;
			this.#kstore_data = where ?? this.#kstore_data;
			this.#count_data_ = times ?? this.#count_data_;
		}
	}
	#sync_exec(_func, _type){
		let _keys = this.#select_type(_type);
		let timer = _func.timer;
		let _call = _func._func;
		let where = _keys.where;
		let max_l = where.length;
		let times = _keys.count - max_l;
		let _init = times;
		for(let i = 0; i < max_l; i++) timer.count(times++, _init).exec && clean_sync_call(_call, where[i]);
		return timer;
	}
	#async_exec(_func, _type){
		let quere = this.#select_type(_type).quere;
			quere.push(_func);
			this.#assign_t(_type, quere);
		return _func.timer;
	}
	add(data, type){
		let _keys = this.#select_type(type), quere = _keys.quere, where = _keys.where, count = _keys.count, times = _keys.times, _init = times;
		quere = quere.filter(_garbage_closed_f);
		quere = quere.map(i => {
			let flags = i.timer.count(times++, _init);
			flags.exec && clean_callback_(i._func, data);
			return flags.keep && i;
		});
		where.push(data);
		if(where.length > count) where.shift();
		this.#assign_t(type, quere, where, times++);
	}
	exec_when(_func, _type, _when){
		let c_set = [this.#sync_exec, this.#async_exec].map(i => i.bind(this));
		if(!check_closed_func(_func)){
			throw new _no_closed_func(_func);
		} else if(check_valid_timer(_func.timer)){
			return c_set[_when & 1](_func, _type);
		} else {
			throw new _invalid_timer_(_func.timer);
		}
	}
	listen(_type = QUERY_BOTH_FLG, _when = _WHEN_BOTH_TM_){
		return new Promise((sucess, onrror) => {
			this.single(_type, _when, sucess, onrror);
		});
	}
	single(_type, _when, _data, _err_){
		let w_set = _generic_parse_(_when, _err_);
		let b_set = _generic_parse_(_type, _err_);
		let c_set = [_data, _err_];
		let r_set = [QUERY_DAT_TYPE, QUERY_ERR_TYPE];
		let e_set = [QUERY_BEFORE_N, QUERY_AFTER_N_]
		for(let i = 0; i < 2; i++) if(b_set[i]){
			let timer = new lookup_hash_timer(TIMER_SINGLE_M);
			for(let j = 0; j < 2; j++) if(w_set[j]){
				try{
					timer = this.exec_when(new lookup_closed_fun(c_set[i], timer), r_set[i], e_set[j]);
				} catch(err){
					console.log(err);
				}
			}
		};
	}
	clear_error(){
		this.#kstore_err_ = new Array();
		return this.#count_error;
	}
}

export {_entry_hash_table as default};
export {
	OPTION_1_ONLY_ as ONLY_OPTION_1,
	OPTION_2_ONLY_ as ONLY_OPTION_2,
	_OPTION_EVERY_ as BOTH_OPTION,
	_WHEN_AFTER_TM as QUERY_AFTER,
	_WHEN_BEFORE_T as QUERY_BEFORE,
	_WHEN_BOTH_TM_ as QUERY_WHENEVER,
	QUERY_DATA_ONL as QUERY_DATA_ONLY,
	QUERY_ERR_ONLY as QUERY_ERROR_ONLY,
	QUERY_BOTH_FLG as QUERY_WHATEVER,
	ERR_N_IS_FUNC_ as MESSAGE_UNKNOWN_FUNCTION,
	ERR_GEN_INV_OP as MESSAGE_UNKNOWN_OPTION,
	ERR_INV_TIMER_ as MESSAGE_UNKNOWN_TIMER,
	ERR_ISN_CLOSED as MESSAGE_UNKNOWN_CALLBACK,
	ERR_BY_CLEANED as MESSAGE_CLEANED_DATABASE
};
export {
_general_error_ as ERROR_GENERIC,
_invalid_option	as ERROR_UNKOWN_OPTION,
_invalid_timer_ as ERROR_UNKOWN_TIMER,
_no_closed_func as ERROR_UNKOWN_CALLBACK,
not_is_function as ERROR_UNKOWN_FUNCTION,
clean_waitlist_ as ERROR_CLEANED_DATABASE,
check_val_func_	as check_function,
clean_sync_call	as sanitise_callback,
clean_callback_	as sanitise_callback_with_async,
_cut_the_bit_at   as cut_the_bit_at,
_generic_parse_   as parse_option,
check_if_nullish_ as check_nullish,
check_valid_timer as check_timer,
lookup_closed_fun as closed_callbak,
check_closed_func as check_callback,
_garbage_closed_f as garbage_callback_filter,
lookup_hash_timer as closed_timer,
make_encapsulated as make_callback,
keep_context_func as keep_context_of
}