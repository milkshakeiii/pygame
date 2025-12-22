#!/usr/bin/env python3
"""
Demo of pyunicodegame library usage.
"""

import pyunicodegame


def update(dt):
    pass


def render():
    root = pyunicodegame.get_window("root")
    root.put_string(10, 5, "Hello, pyunicodegame!", (0, 255, 0))
    root.put(10, 7, "@", (255, 255, 0))


def on_key(key):
    pass


def main():
    pyunicodegame.init("pyunicodegame Demo", width=80, height=30, bg=(20, 20, 30, 255))
    pyunicodegame.run(update=update, render=render, on_key=on_key)


if __name__ == "__main__":
    main()
