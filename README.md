# PyRobbo

PyRobbo is a Pygame remake of *Robbo*, the puzzle game for 8-bit Atari
computers. Guide a small robot across hostile planets, collecting the screws
needed to repair its escape capsule. When the screw counter reaches zero, the
capsule starts to blink. Walk into it to reach the next planet.

![Robbo on the first planet, with nine screws left to collect][first-planet]

## Install and play

To play the version in this repository, clone it and create a Python 3 virtual
environment.

```sh
git clone https://github.com/macdems/pyrobbo.git
cd pyrobbo
python -m venv .venv
```

Activate the environment with `. .venv/bin/activate` on Linux or macOS, or
`.\.venv\Scripts\Activate.ps1` in Windows PowerShell. Then install and launch
the game in a window.

```sh
python -m pip install "setuptools<81" .
pyrobbo --window
```

The setuptools pin supplies `pkg_resources`, which the game uses to load its
assets. For published releases, see [PyRobbo on PyPI][pypi].

## Choose a planet

For a first game, select **original**, **level 1**, and press **Enter**. On this
board the ammunition clip is two squares to Robbo's right. Pick it up for nine
shots. The counters along the bottom show screws remaining, keys held,
ammunition, and the current level, from left to right.

| Level set | Levels | What to expect |
| --- | ---: | --- |
| `original` | 58 | The classic campaign. |
| `forever` | 59 | A longer, tougher set of puzzles. |

In the menu, use **Up/Down** to select a row and **Left/Right** to change its
value. The **Theme** row switches between `default`, `oily`, and `tronic`. The
robot and board preview update as you browse. You can also click the arrows
and **Start Level**, or navigate with a joystick's stick or D-pad and press its
first button to start.

PyRobbo remembers your theme and the last level played in each set. Returning
to a level starts the puzzle from its initial layout.

## Controls

| During play | Keyboard |
| --- | --- |
| Move | Arrow keys or **WASD** |
| Fire | Hold **Shift** and press a direction |
| Scroll a tall board | Hold **Ctrl** and press **Up/Down** or **W/S** |
| Restart the level | **Ctrl+R** or **Ctrl+X** |
| Jump to a level in this set | **Ctrl+L**, then two digits, e.g. **07** |
| Adjust speed | **+** or **=** to speed up, **-** to slow down |
| Toggle sound | **Ctrl+M** |
| Toggle clever bear movement | **Ctrl+B** |
| Toggle fullscreen | **F** (also works in the menu) |
| Return to the menu | **Esc** |
| Quit | **Ctrl+Q**, or **Esc** from the menu |

With a joystick, move with the stick. Hold the first button and push the stick
in the direction you want to fire. Hold the second button and move the stick
up or down to look ahead on a tall board.

## Make a level set

A level set is a plain-text `.dat` file. To try a one-room puzzle, save this as
`first-orbit.dat`.

```text
[level]
1
[data]
OOOOOOOOO
OR.%D.T!O
OOOOOOOOO
[end]
```

Move right from Robbo (`R`), collect the key (`%`), and use it to open the door
(`D`). The screw (`T`) activates the capsule (`!`). The outer walls are the
letter `O`, and dots mark empty squares.

```sh
pyrobbo first-orbit.dat
```

This copies the file into your user level directory and selects **first-orbit**
in the menu. Add another `[level]` through `[end]` block to extend the set.
For examples with teleports, enemies, and moving guns, see the
[bundled level files][level-files].

On Linux, the default locations are `~/.local/share/pyrobbo/levels/` for
installed sets and `~/.config/pyrobbo.yml` for settings. To start with a
particular theme or display mode, use a command such as
`pyrobbo --fullscreen --skin tronic`. Run `pyrobbo --help` for all options.

## Credits and license

Janusz Pelc wrote the original *Robbo* for the Atari XE/XL, published by
L.K. Avalon. Maciej Dems developed this Pygame remake. Graphics and level data
come from [GNU Robbo][gnu-robbo].

PyRobbo is free software under the [GNU General Public License][license],
version 3 or later.

[first-planet]: docs/images/original-level-01.png
[pypi]: https://pypi.org/project/PyRobbo/
[level-files]: robbo/levels/
[gnu-robbo]: https://sourceforge.net/projects/gnurobbo/
[license]: LICENSE
