function make_context(width, height, background = 'black') {
	let a = document.createElement('canvas');
	a.width = (width && Number(width)) || a.width;
	a.height = (height && Number(height)) || a.height;
	let ctx = a.getContext('2d');
	ctx.fillStyle = background;
	ctx.fillRect(0, 0, a.width, a.height);
	return {ctx: ctx, src: a}
}
function one_time_context(src, width, height, background = 'black') {
	width = width || src.width;
	height = height || src.height;
	let a = make_context(width, height, background);
	a.ctx.drawImage(src, 0, 0, a.src.width, a.src.height);
	return a;
}
function imgToBlob(ctx, type = 'image/png', quality = 1) {
	return new Promise(function (suc, rej) {
		ctx.toBlob(function (data) {
			if (data === null || data === undefined) {
				rej()
			} else {
				suc(data)
			}
		}, type, quality)
	})
}
function raw_as_url(data, callback) {
	let src = URL.createObjectURL(data);
	return new Promise(function (res, rej) {
		Promise.resolve(src).then(data => res(data))
		.then(function () { URL.revokeObjectURL(src) })
		.catch(function () { URL.revokeObjectURL(src) }).catch(e => rej(e))
	})
}
function download_raw(data, filename) {
	let src = URL.createObjectURL(data);
	try {
		let a = document.createElement('a');
		a.addEventListener('download', function () {
			URL.revokeObjectURL(src);
		})
		a.href = src;
		a.download = filename;
		a.click();	
	} catch (e) {
		URL.revokeObjectURL()
	}
}
