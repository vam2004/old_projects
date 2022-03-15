function complex(a, b){
	this.a = a;
	this.b = b;
	
}
/*
function cut(x){
	var pi2 = 2 * Math.PI;
	return x - Math.floor(x / pi2) * pi2;
}
*/
class arccong{
	"use strict";
	static lib = ((slf) => {
		let obj = {
			reduce: function(x){
				return new slf(0, x.mod, x.unit)
			},
			clone: function(x){
				return new slf(x.rev, x.mod, x.unit);
			},
			from: function(x, unit = 1){
				let rev	= Math.floor(x / unit);
				let mod	= x - rev * unit;
				return new slf(rev, mod, unit);
			},
			convert: function(x, unit = 1){
				if(x.unit == unit){
					return obj.clone(x);
				} 
				let rev	= Math.floor((x.unit / unit) * x.rev + x.mod / unit);
				let mod	= (x.unit * x.rev - rev * unit) + x.mod;
				return new slf(rev, mod, unit)
			},
			retrieve: function(x){
				return x.unit * x.rev + x.mod
			},
			add: function(x, y, unit = x.unit || 1){
				let mx = obj.convert(x, unit);
				let my = obj.convert(y, unit);
				let it = obj.from(mx.mod + my.mod, unit);
				return new slf(mx.rev + my.rev + it.rev, it.mod, unit);
			},
			mul2: function(x, y, unit = 1){
				let mx = obj.convert(mx, unit);
				let my = obj.convert(y, unit);
				let l0 = obj.from(mx.mod * my.rev, unit);
				let l1 = obj.from(mx.rev * my.mod, unit);
				let l2 = obj.from(mx.mod * my.mod, unit);
				let v0 = obj.from((l1.mod + l2.mod) * unit, unit);
				return new slf(mx.rev * my.rev * unit + (l0.rev + l1.rev) * unit + l2.rev, v0.mod + l2.mod, unit);
			},
			sumOn: function(x, ...args){
				let mx = obj.clone(x);
				let unit = mx.unit;
				args.forEach(i=> mx = obj.add(mx, i, unit));
				return mx;
			},
			mulOn: function(x, ...args){
				let mx = obj.clone(first);
				args.forEach(i=>{
					mx = obj.mul2(mx, i);
				});
				return mx;
			},
			addValueOn: function(x, y, unit = x.unit || 1){
				return obj.add(x, obj.from(y, unit), unit);
			},
			sumValuesOn: function(x, ...args){
				let mx = obj.clone(x);
				let unit = mx.unit;
				args.forEach(i => mx = obj.addValueOn(mx, i, unit))
				return mx;
			},
			addValues: function(x, y, unit = 1){
				return obj.add(obj.from(x, unit), obj.from(y, unit), unit);
			},
			sumValues: function(unit = 1, ...args){
				return obj.sumValuesOn(new slf(0, 0, unit), [...args]);
			},
			sum: function(unit = 1, ...args){
				return obj.sumOn( ew slf(0, 0, unit), [...args]);
			},
			mul: function(unit = 1, x = obj.from(1, unit), ...args){
				return obj.mulOn(obj.convert(x, unit), [...args]);
			},
			addRev: function(x, y, unit = x.rev || 1){
				let my = new slf(y, 0, unit);
				return obj.add(x, my, unit);
			},
		}
		return obj;
	})(this);
	own = ((slf) => {
		return slf.constructor.lib;
	})(this)
	constructor(rev, mod, unit = 1){
		this.rev = rev;
		this.mod = mod;
		this.unit = unit;
	}
	convert(unit = 1){
		return this.own.convert(this, unit = 1);
	}
	addWith(x){
		return this.own.add(this, x, this.unit);
	}
	addValue(x){
		return this.own.addValueOn(this, x);
	}
	sumValues(...args){
		return this.own.sumValuesOn(this, [...args]);
	}
	sumWith(...args){
		return this.own.sum(this.unit, [...args]);
	}
	retrieve(){
		return this.own.retrieve(this);
	}
	from(x, unit = unit){
		return this.own.from(x, unit).
	}
	clone(x){
		return this.own.clone(this);
	}
	paste(x){
		return x.clone(this);
	}
	mulWith(x){
		return this.own.mulOn(this, x).
	}
	mul(...args){
		return this.own.mul(this.unit, this, [...args]).
	}
	addRev(y, unit = this.unit){
		return this.own.addRev(this, y, unit);
	}
	reduce(){
		return this.own.reduce(this);
	}
}
class complex{
	static trigonometric = ((root, arclib) => {
		return class complexTrigonometric{
			static lib = ((slf, arclib) => {
				function r_hhrt(x, n = 2){
					return Math.exp(Math.log(x) / n)
				}
				const pi2 = Math.PI * 2;
				const pi = Math.PI;
				let obj = {
					retrieve: function(x){//retrieve to a complex number (regular form);
						return new root(obj.real(x), obj.imag(x));
					},
					from: function(x){//from a complex number (regular form);
						return new slf(Math.hypot(x.a, x.b), Math.atan2(x.a, x.b));
					},
					nhrt: function(x, n = 2){
						let result = new Array();
						let arc0 = arclib.from(x.argz / n, pi2);
						let rot = arclib.from(pi2 / n);
						let mod = r_nhrt(root.modz, n);
						let now = arc0;
						for(var i = 0; i < n; i++){
							result.push(now);
							now = arclib.add(now, rot, pi2)
						}
						return result.map(i => new slf(mod, i.mod, i.rev + x.rev))
					},
					real: function(x){
						return x.modz * Math.cos(x.argz);
					},
					imag: function(x){
						return  x.argz * Math.sin(x.argz);
					},
					mul2: function(x, y){
						let arc = arclib.add(obj.arg_as_arc(x), obj.arg_as_arc(y))
						return new slf(x.modz * y.modz, );
					},
					arg_as_arc: function(x){
						let it = arclib.from(x.argz, pi2);
						return arclib.addRev(it, x.rev, pi2);
					}
				}
				return obj;
			})(complexTrigonometric, arclib);
			own = ((slf)=>{
				return slf.constructor.lib;
			})(this);
			constructor(mod, arg, rev = 0){
				this.argz = arg;
				this.modz = mod;
				this.rev = rev;
			}
			from(x){
				return this.own.from(x)
			}
			nhrt(n){
				return this.own.nhrt(this, n)
			}
			retrieve(){
				return this.own.retrieve(this);
			}
			get real(){
				return this.own.real(this);
			}
			get imag(){
				return this.own.imag(this);
			}
		}
	})(this, arccong);
	static lib = ((slf, arclib, trigonometric) => {
		let obj = {
			nhrt: function(x, n){
				return trigonometric.from(x).nhrt(n).retrieve();
			},
			abs: function(x){
				return Math.hypot(x.a, x.b);
			},
			arg: function(x){
				return Math.atan2(x.a, x.b);
			},
			mul2: function(x, y){
				return new slf(x.real * y.real - x.imag * y.imag, x.real * y.imag + x.imag * y.real);
			},
			mul: function(x = new slf(1, 0), ...args){
				let now = x;
				args.forEach(i => now = obj.mul2(now, i));
				return now;
			}
		}
		return obj;
	})(this, arccong, trigonometric);
	own = ((slf)=>{
		return slf.constructor.lib;
	})(this);
	own_t = ((slf)=>{
		return slf.constructor.trigonometric;
	})(this);
	constructor(a, b){
		this.real = a;
		this.imag = b;
	}
	toTrigonometric(){
		return this.own_t.from(this);
	}
}
complex.prototype = {
	PI2: 2 * Math.PI; 
	utils: {
		r_nhrt: function(x, n = 2){
			return Math.exp(Math.log(x) / n);
		},
		c_nhrt: function(c, n = 2){
			var seg		= c.utils.seg;
			var pi2		= c.PI2
			var result	= new Array();
			var abs		= c.utils.nhrt(c.mod());
			var base	= seg((c.arg() / n), pi2);
			var pi_n	= pi2 / n
			for(var i = 0; i < n; i++){
				result.push(seg((base + pi_n * i), pi2))
				// seg(x + y, k) = seg(seg(x, k) + seg(y, k), k)
			}
		}
	}
	
}

function quadratic_eq(a, b, c){
	
}
/*
n := i + j * 2PI, 0 <= i < 2PI, j in Z <> cut(n) := i <> cut(i) = cut(n) = cut(cut(n)) = i
n + k := (i + k) + j * 2PI, j in Z, (i + k) := m + l * 2PI, l in Z, 0 <= m < 2Pi -> n + k = m + (l + j) * 2PI -> cut(n + k) = cut(i + k)

cut(n) := i -> cut(n) = cut(i) -> cut(n + k) = cut(i + k)
therefore: cut(n + k) = cut(cut(n) + k)

cut(y) = cut(x) = i -> cut(y + k) = cut(i + k), cut(x + k) = cut(i + k) -> cut(y + k) = cut(x + k)

cut(n + k) = cut(cut(n) + k) -> cut(k + cut(n)) = cut(cut(n) + cut(k)) -> cut(n + k) = cut(cut(n) + cut(k))

cut(k) = 0 -> cut(n + k) = cut(cut(n)) = cut(n)

cut(x) = 0 -> x = j * 2PI, j in Z

cut(0) = cut(x - x) = cut(cut(-x) + cut(x)) -> cut(-x) + cut(x) = j * 2PI, j in Z

****************************************************************
arg(nhrt(z, k)) := (arg(z) + k * 2PI) / n, k = 0 ...  n - 1
abs(nhrt(z, k)) := nhrt(abs(z), n), k = 0 ...  n - 1
****************************************************************
arg(nhrt(z, k)) := j(k) + i(k) * 2PI, i(k) in Z, 0 <= j(k) < 2PI in R, , k = 0 ...  n - 1
arg(nhrt(z, k)) := (arg(z) / n) + (k * 2PI / n)
arg(nhrt(z, k + 1)) := (arg(z) / n) + ((k + 1) * 2PI / n)
arg(nhrt(z, k + 1)) := (arg(z) / n) + (k * 2PI / n) + (2PI / n)
arg(nhrt(z, k + 1)) := arg(nhrt(z, k)) + (2PI / n)

cut(arg(nhrt(z, k + 1))) := cut(cut(arg(nhrt(z, k))) + cut((2PI / n)))
cut(arg(nhrt(z, k))) := cut(cut(arg(z) / n) + cut(k * 2PI / n))
*/


//x == x.rev * unit + x.mod
//y == y.rev * unit + y.mod
//x * y == (x.rev * unit + x.mod) * (y.rev * unit + y.mod)
//x * y == (x.rev * y.rev) * [unit^2] + (x.rev * y.mod) * [unit] + (x.mod * y.rev) * [unit] + (x.mod * y.mod)
//x * y == (x.rev * y.rev) * [unit^2] + [unit] * ([x.rev * y.mod] + [x.mod * y.rev]) + (x.mod * y.mod)
/*
x * y == (it.rev + mx.rev * my.rev * unit) * unit + it.mod
it ==  [unit] * ([x.rev * y.mod] + [x.mod * y.rev]) + (x.mod * y.mod)
l0 == mx.rev * my.rev		l1 == mx.rev * my.mod
l2 == mx.mod * my.rev		l3 == mx.mod * my.mod
v0 == l0 * unit^2			v1 == (l1 + l2) * unit
v2 == (l1 + l2) * unit
v2 == (l1.mod+l2.mod)*unit	mx * my == v0 + v1 + l3
v1 == (l1.rev + l2.rev) * unit + v2
v1.rev == l1.rev + l2.rev + v2.rev
v1.rev == v2.mod == mod((l1.mod+l2.mod)*unit)
v0.rev == l0.rev * unit == mx.rev * my.rev * unit
rs == x * y == mx * my
rs.mod == v1.mod + l3.mod
rs.rev == v0.rev + v1.rev + l3.rev
*/

// vx == mx.rev * unit + mx.mod
// vy == my.rev * unit + my.mod
// mx.mod + my.mod == it.rev * unit + it.mod
// sum == vx + vy == (mx.rev + my.rev ) * unit + (mx.mod + my.mod) == (mx.rev + my.rev + it.rev) * unit + it.mod

/*				
class base{
	"use strict";
	static counter = 0;
	static lib = ((slf) => {
		var obj = {
			create: function(){
				var count = slf.counter++;
				return new slf(count);
			},
			log: function(){
				console.log(obj.create())
			}
		}
        return obj;
	})(this);
	own = ((slf) => {
		return slf
	})(base)
	constructor(a){
		this.a = a;
		console.log(this.own)
	}
}
*/