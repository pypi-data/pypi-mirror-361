# collide_circle

A simple Pygame utility for detecting collisions between rectangles and circles.

## 📦 Installation

Install from PyPI (after publishing):

```bash
pip install collide_circle





#Or install locally (from source):
pip install .




#Usage

import pygame
from collide_circle import rect_collides_with_circle

# Example Pygame setup
rect = pygame.Rect(100, 100, 80, 60)
circle_center = (150, 120)
circle_radius = 40

if rect_collides_with_circle(rect, circle_center, circle_radius):
    print("Collision detected!")


#Function

rect_collides_with_circle(rect, circle_center, circle_radius)
