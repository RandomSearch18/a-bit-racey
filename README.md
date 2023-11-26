# A Bit Racey

> A car-themed arcade game built using the power of Pygame 

This is our first Pygame project. It is based on the tutorial at <https://pythonprogramming.net/pygame-python-3-part-1-intro/>, although I have implemented it in an object-oriented way (along with other changes to the program's design).

## Usage

Start by cloning this repository to a folder of your choice. Commands in this guide assume the working directory is set to the root of this repository.

In general, you'll need Python 3.8 or above, and the `pygame` Python package available. For the platforms that I've tested the game on, there are some specific instructions below.

### Arch Linux

1. Install the `python` and `python-pygame` packages, e.g. by running `sudo pacman -S python python-pygame`
2. Run the game: `python3 main.py`

### Android (Termux)

The game seems to work under Android using [Termux](https://termux.dev/) with the experimental [Termux:X11](https://github.com/termux/termux-x11) add-on. Start by installing the dependencies:
<!-- Pygame dependencies source: https://www.reddit.com/r/termux/comments/ks6xi4/pygame_on_termux/ -->
```bash
$ pkg install python
$ pkg install sdl2 sdl2-image sdl2-ttf xorgproto # Libaries required by pygame
$ pip install pygame
```

Then, launch an X11 session ([see the Termux:X11 documentation for guidance](https://github.com/termux/termux-x11#running-graphical-applications)) and start the game:
```bash
$ python3 main.py
```

### PostmarketOS

Note: This should also work for Alpine Linux in general, although you may have to replace `sudo` with whatever tool your system uses for elevating permissions, e.g. `doas`.

```sh
$ sudo apk add python3 py3-pygame
$ python3 main.py
```

### Zorin OS

These instructions should also work on Ubuntu 20.04 LTS, which Zorin OS is based on.

```bash
$ sudo apt install python3 python3-pygame
$ python3 main.py
```

## Tips

### Desktop entry

To avoid having to start the game from the terminal, you can create a [desktop entry](https://wiki.archlinux.org/title/desktop_entries) to launch it from your applications menu. Be sure to use the absolute path to Python and set `Path` to the root of this repository (so that the game can find its assets). A simple example is shown below (replace `/path/to/` with the actual path to the cloned repository):
```desktop
[Desktop Entry]
Type=Application
Name=A Bit Racey
Exec=/usr/bin/python3 /path/to/a-bit-racey/main.py
Path=/path/to/a-bit-racey/
Terminal=false
Categories=Game;
```
