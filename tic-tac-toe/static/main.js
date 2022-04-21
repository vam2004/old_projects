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
		"option_o": svg_url_spec + "PHN2ZyB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiB4bWxucz0i"+"aHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgoJPGNpcmNsZSBjeD0iNTAlIiBjeT"+"0iNTAlIiByPSIyNSUiIHN0cm9rZT0iIzFiNGFiNyIgc3Ryb2tlLXdpZHRoPSIxMiUi"+"IGZpbGw9InRyYW5zcGFyZW50Ij48L2NpcmNsZT4KPC9zdmc+",
		"option_x": svg_url_spec +  "PHN2ZyB2ZXJzaW9uPSIxLjEiIHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiB4bWxucz0i"+"aHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgoJPGRlZnM+CgkJPGcgaWQ9Im15X3"+"giIHg9IjAiIHk9IjAiIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGNvbG9yPSIj"+"MWI0YWI3Ij4KCQkJPHJlY3QgeD0iMTIlIiB5PSI0MiUiIHdpZHRoPSI3NiUiIGhlaW"+"dodD0iMTYlIiByeD0iNS41JSIgcnk9IjMlIiBmaWxsPSJjdXJyZW50Y29sb3IiIHN0"+"cm9rZT0idHJhbnNwYXJlbnQiPjwvcmVjdD4KCQk8L2c+Cgk8L2RlZnM+Cgk8dXNlIG"+"hyZWY9IiNteV94IiB0cmFuc2Zvcm09InJvdGF0ZSg0NSwgNzUsIDc1KSIvPgoJPHVz"+"ZSBocmVmPSIjbXlfeCIgdHJhbnNmb3JtPSJyb3RhdGUoMTM1LCA3NSwgNzUpIi8+Cj"+"wvc3ZnPg==",
		//"undo": svg_url_spec + 
		//"redo": svg_url_spec +
		//"exit": svg_url_spec +
		//"join": svg_url_spec +
		//"pause": svg_url_spec +
		//"friends": svg_url_spec +
		//"config": svg_url_spec +
		//"profile": svg_url_spec +
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
		const self = this;
		this.cells = cells;
		const cells_handlers = Array.prototype.map.call(this.cells, function(target, index) {
			target.addEventListener("click", function (evt) {
				evt.preventDefault();
				self.load_cell_id(index);
			});
		});
		this.cells_handlers = cells_handlers;
		this.options = []
		this.can_replace = true
		this.can_play = true
		this.can_choose = true
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
	load_cell(id, selection) {
		const cell = this.cells[id];
		this.clear_cell(cell);
		load_cell_image(cell, selection);
	}
	load_cell_id(id) {
		const selection = this.get_current_selection();
		this.load_cell(id, selection);
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
const selection_contents = [assets.options.option_o, assets.options.option_x, null];
class game_menu {
	constructor(menus, game) {
		this.menus = menus;
		this.game = game
		this.allow_select = true;
		this.previous_target = null;
		this.cache = selection_contents
		const self = this;
		const menus_handlers = Array.prototype.map.call(this.menus, function(target, id){
			target.addEventListener("click", function (evt) {
				evt.preventDefault();
				if (self.game.can_choose) {
					evt.target.style.setProperty("background-color", "#532e07");
					if (is_not_nullish(self.previous_target) && self.previous_target != evt.target) {
						self.previous_target.style.setProperty("background-color", "");
					}
					self.previous_target = evt.target;
					self.game.set_current_selection(self.cache[id])
				}
			});
		});
		this.menus_handlers = menus_handlers;
	}
}
function sane_class_config(config, key) {
	if (is_not_nullish(config) && is_not_nullish(config[key])) {
		return config[key];
	} else {
		return "";
	}
}
function range_map(callback, init, end, step) {
	const inner_step = step || 1;
	tmp = [];
	if (init < end) {
		let idx = init;
		while(idx < end) {
			tmp.push(callback(idx));
			idx += inner_step;
		}
	} else {
		throw RangeError();
	}
	return tmp
}
function create_game(config) {
	const game = document.createElement("div")
	game.className = sane_class_config(config, "primary_class");
	const selections = create_selections(selection_contents, config);
	game.appendChild(selections);
	const game_table = document.createElement("table")
	game_table.className = sane_class_config(config, "game_table_class");
	const game_cells = range_map(function() {
		const cell = document.createElement("th");
		cell.className = sane_class_config(config, "game_cells_class");
		return cell;
	}, 0, 9);
	const game_rows = range_map(function (idx) {
		const row = document.createElement("tr");
		row.className = sane_class_config(config, "game_rows_class");
		for (x of game_cells.slice(3 * idx, 3 * idx + 3)) {
			row.appendChild(x);
		}
		game_table.appendChild(row);
		return row;
	}, 0, 3);
	game.appendChild(game_table);
	return game;
}
function create_selection(src, config) {
	const menu_div = document.createElement("div");
	menu_div.className = sane_class_config(config, "selection_secondary_class");
	if (is_not_nullish(src)) {
		const inner = src.cloneNode();
		inner.className = sane_class_config(config, "selection_class");
		menu_div.appendChild(inner);
	}
	return menu_div
}
function create_selections(src, config) {
	const selection_ctn = document.createElement("div")
	selection_ctn.className = sane_class_config(config, "selection_primary_class");
	const selections = range_map(function (idx) {
		const inner = create_selection(src[idx], config);
		selection_ctn.appendChild(inner);
	}, 0, src.length);
	return selection_ctn;
}

const game_spec = {
	primary_class: "game",
	game_table_class: "game", 
	game_cells_class: "game",  
	game_rows_class: "",
	selection_primary_class: "game-options",
	selection_secondary_class: "game-opt",
	selection_class: "game-opt"
}
const game_dyn = create_game(game_spec);
document.body.appendChild(game_dyn)
const cells = document.querySelectorAll("th.game");
const my_game = new game_gui(cells);
const menus = document.querySelectorAll("div.game-opt");
const my_menus = new game_menu(menus, my_game);