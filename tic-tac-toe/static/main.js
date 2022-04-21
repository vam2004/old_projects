function clear_childs(ele) {
	while (ele.firstChild != null) {
		ele.removeChild(ele.lastChild);
	}
}
function is_not_nullish(src) {
	return src != undefined && src != null;
}
function process_image(src, width, height) {
	var tmp = new Image(width, height)
	tmp.src = src
	return tmp
}
function load_cell_image(cell, img) {
	if(cell.firstChild == null && is_not_nullish(img)) {
		let tmp = img.cloneNode();
		cell.appendChild(tmp);
	}
}
function make_assets () {
	const svg_url_spec = "data:image/svg+xml;base64,"
	const assets_groups = {
		"options": {
			"width": 100,
			"height": 100,
			"inner": ["option_o", "option_x"]
		}
	}
	const raw_assets = {
		"option_o": svg_url_spec + "PHN2ZyB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgoJPGNpcmNsZSBjeD0iNTAlIiBjeT0iNTAlIiByPSIyNSUiIHN0cm9rZT0iIzFiNGFiNyIgc3Ryb2tlLXdpZHRoPSIxMiUiIGZpbGw9InRyYW5zcGFyZW50Ij48L2NpcmNsZT4KPC9zdmc+",
		"option_x": svg_url_spec +  "PHN2ZyB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgoJPGRlZnM+CgkJPGcgaWQ9Im15X3giIHg9IjAiIHk9IjAiIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGNvbG9yPSIjMWI0YWI3Ij4KCQkJPHJlY3QgeD0iMTIlIiB5PSI0MiUiIHdpZHRoPSI3NiUiIGhlaWdodD0iMTYlIiByeD0iNS41JSIgcnk9IjMlIiBmaWxsPSJjdXJyZW50Y29sb3IiIHN0cm9rZT0idHJhbnNwYXJlbnQiPjwvcmVjdD4KCQk8L2c+Cgk8L2RlZnM+Cgk8dXNlIGhyZWY9IiNteV94IiB0cmFuc2Zvcm09InJvdGF0ZSg0NSwgNzUsIDc1KSIvPgoJPHVzZSBocmVmPSIjbXlfeCIgdHJhbnNmb3JtPSJyb3RhdGUoMTM1LCA3NSwgNzUpIi8+Cjwvc3ZnPg=="
	}
	function process_assets(assets_groups, assets_srcs) {
		var result = {};
		for (const k in assets_groups) {
			const tmp = assets_groups[k];
			const width = tmp["width"];
			const height = tmp["height"];
			let inner = {};
			for (i of tmp["inner"]) {
				let src = assets_srcs[i];
				if (is_not_nullish(src)) {
					inner[i] = process_image(src, width, height);
				}
			}
			result[k] = inner;
		}
		return result;
	}
	return process_assets(assets_groups, raw_assets);
}
const assets = make_assets();
class game_gui {
	constructor(cells) {
		this.cells = cells;
		const cells_handlers = Array.prototype.map.call(this.cells, function(target, index) {
				target.addEventListener("click", function (evt) {
				evt.preventDefault();
				my_game.load_cell_id(index);
			});
		});
		this.cells_handlers = cells_handlers;
		this.options = []
		this.can_replace = true
		this.can_play = false
		this.can_choose = false
		this.current_choice = null
		this.animated_cannot_replace = []
	}
	set_current_selection(selection) {
		this.current_choice = selection;
	}
	get_current_selection() {
		if (is_not_nullish(this.current_choice)) {
			return this.current_choice
		} else {
			return null;
		}
	}
	load_cell_id(id) {
		const cell = this.cells[id];
		const selection = this.get_current_selection();
		this.clear_cell(cell);
		load_cell_image(cell, selection);
	}
	clear_cell(cell) {
		if (this.can_replace) {
			clear_childs(cell);
		} else if (cell.firstChild != null) {
			this.animate_cannot_replace(cell)
		}
	}
	animate_cannot_replace(cell) {
		if(this.animated_cannot_replace.indexOf(cell) == -1) {
			this.animated_cannot_replace.push(cell);
			const self = this;
			cell.style.setProperty("background-color", "#563022");
			window.setTimeout(function() {
				cell.style.setProperty("background-color", "");
				let index = self.animated_cannot_replace.indexOf(cell);
				self.animated_cannot_replace.splice(index, 1);
			}, 150);
		}
	}
}
const cells = document.querySelectorAll("th.game");
const my_game = new game_gui(cells);
class game_menu {
	constructor(menus, game) {
		this.menus = menus;
		this.game = game
		this.allow_select = true;
		this.previous_target = null;
		this.cache = [assets.options.option_o, assets.options.option_x, null];
		const self = this;
		const menus_handlers = Array.prototype.map.call(this.menus, function(target, id){
			target.addEventListener("click", function (evt) {
				evt.preventDefault();
				if (self.allow_select) {
					evt.target.style.setProperty("background-color", "#532e07");
					if (is_not_nullish(self.previous_target) && self.previous_target != evt.target) {
						self.previous_target.style.setProperty("background-color", "");
					}
					self.previous_target = evt.target;
					game.set_current_selection(self.cache[id])
				}
			});
		});
		this.menus_handlers = menus_handlers;
	}
}
const menus = document.querySelectorAll("div.game-opt");
const my_menus = new game_menu(menus, my_game);
