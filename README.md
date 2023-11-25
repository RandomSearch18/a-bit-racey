# A Bit Racey

> A car-themed arcade game built using the power of Pygame 

This is our first Pygame project. It is based on the tutorial at <https://pythonprogramming.net/pygame-python-3-part-1-intro/>, although I have implemented it in an object-oriented way (along with other changes to the program's design).

## Usage

Start by cloning this repository to a folder of your choice. Commands in this guide assume the working directory is set to the root of this repository.

In general, you'll need Python 3.8 or above, and the `pygame` Python package available. For the platforms that I've tested the game on, there are some specific instructions below.

### PostmarketOS

Note: This should also work for Alpine Linux in general, although you may have to replace `sudo` with whatever tool your system uses for elevating permissions, e.g. `doas`.

```sh
$ sudo apk add python3 py3-pygame
$ python3 main.py
```

### Zorin OS

These instructions should also work on Ubuntu 20.04 LTS, which Zorin OS is based on.

```sh
$ sudo apt install python3 python3-pygame
$ python3 main.py
```
