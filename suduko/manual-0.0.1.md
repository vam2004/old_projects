# Version Notes
This is a manual for the pre-alpha version. Before using whatever information associated with this, consider the possibily of it was changed without notification, also it is unstable. If you notice a bug, let us (which is only me at this time) now.
## Known Errors
- The generation could lead to a impossible solution, I noticied it when generating the 81 possible units, also I suppose that will likely happens when the number of generated units is lesser than asked
## Non-Implemeted Features
- Graphical interface, maybe with Gtk or Js/Html/Css
- Server Support (allow others interfaces)
- Full-functional Generator
- Serialization/Deserialization, maybe with SQLite
- Full-functional Transactional Model
- Multiplayer
## Contributing
If you want to contribute, then you should:
- Clone the project if you want to use a incompatible license
- Otherwise use Lesser General Public License (with the same version), if you want to edit directly to this repository
# Manual
There aren's command line argument yet, but it haves a interactive mode (with suduko_interative.py).
To enter in the game you could ony run
```bash
python3 suduko_interative.py
```
if the Python executable is named `python`, the you should run as:
```bash
python suduko_interative.py
```
Then you will enter in the interactive mode.
# Interactive Mode
The interactive mode start likely with the following prompt:
```
Next:
```
You can type either a moviment or a action (prefixed with `do` keyword). 
## Actions
These are the actions avaliable:
- `do generate <option1> <option2>`:
+ if the `option1` is `--default` or when both options aren't selected, the app choice the default amount, otherwise, it will be the maximum amount of generated cells. It will use all non-nulls cells intead of generating even more (but it have a bug and therefore can change these). The last option indicates the seed, by default the system choice one.
+ `do clear`:
Clear all units (reset the game)
- `do list-all`:
Show all units
- `do set-replace <replace>`:
Set the string used to represent empty cells
- `do auto-list`:
Eneable showing the game after a moviment

## Moviment
There are two ways of inseting a element on the game:
- `cr <column> <row> v <value>`
- `gp <grid> <grid-pos> v <value>`

## Errors:
There are several errors which can happens when you was playing, which can be internal error, a invalid input, or a non-user-friendly way of showing that something is wrong
 