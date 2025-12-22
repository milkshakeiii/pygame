#!/usr/bin/env python3
"""
Demo of the EffectSprite system.

Click or press Space to spawn particles with velocity, drag, and fade.
"""

import random
import pygame
import pyunicodegame


def main():
    root = pyunicodegame.init("Effect Demo", width=60, height=30, bg=(10, 10, 20, 255))

    spawn_x = 30
    spawn_y = 15

    def spawn_particles(x, y, count=10):
        """Spawn a burst of particles."""
        chars = ['*', '+', '.', '·', '°']
        colors = [
            (255, 200, 50),   # Yellow
            (255, 150, 30),   # Orange
            (255, 100, 20),   # Red-orange
            (255, 255, 100),  # Bright yellow
        ]

        for _ in range(count):
            char = random.choice(chars)
            fg = random.choice(colors)
            vx = random.uniform(-8, 8)
            vy = random.uniform(-12, -4)  # Mostly upward
            drag = random.uniform(0.2, 0.5)
            fade_time = random.uniform(0.5, 1.5)

            effect = pyunicodegame.create_effect(
                char, x=x, y=y, vx=vx, vy=vy,
                fg=fg, drag=drag, fade_time=fade_time
            )
            root.add_sprite(effect)

    def on_key(key):
        nonlocal spawn_x, spawn_y
        if key == pygame.K_SPACE:
            spawn_particles(spawn_x, spawn_y)
        elif key == pygame.K_LEFT:
            spawn_x = max(5, spawn_x - 1)
        elif key == pygame.K_RIGHT:
            spawn_x = min(55, spawn_x + 1)
        elif key == pygame.K_UP:
            spawn_y = max(5, spawn_y - 1)
        elif key == pygame.K_DOWN:
            spawn_y = min(25, spawn_y + 1)
        elif key == pygame.K_q:
            pyunicodegame.quit()

    def update(dt):
        root.update_sprites(dt)

    def render():
        # Draw spawn point indicator
        root.put(spawn_x, spawn_y, '+', (100, 100, 100))

        # Draw instructions
        root.put_string(1, 1, "Space: spawn particles  Arrows: move spawn point  Q: quit", (80, 80, 80))

        # Show particle count
        count = len(root._sprites)
        root.put_string(1, 28, f"Particles: {count}", (80, 80, 80))

        root.draw_sprites()

    pyunicodegame.run(update=update, render=render, on_key=on_key)


if __name__ == "__main__":
    main()
