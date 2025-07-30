# PySick

PySick - A Bypass for learning Graphics Development

Classes:

- SickError — Custom error for PySick
- InGine — Main engine/window class
- graphics — Drawing utility class
- message_box — Messagebox utilities
- keys — Keyboard input tracking
- colliCheck — Collision detection utilities
- image — Display images and video on canvas

---

## Description

PySick is a lightweight Python library designed to simplify learning graphics development.

It provides easy functions for:

- Creating a window
- Drawing shapes using RGB or RGBA tuples
- Filling the canvas with color
- Collision detection (rect vs rect, circle vs circle, rect vs circle)
- Displaying images and videos
- Message box dialogs
- Real-time keyboard and mouse input (press, hold)
- Running interactive loops like game engines

Built on top of Tkinter, PySick removes boilerplate so you can focus on graphics logic.

---

## Installation

If packaged, install via pip:

```bash
pip install pysick
```

Otherwise, place the `pysick` folder into your Python project directory.

---

## Quick Example

```python
import pysick

pysick.ingine.init(800, 600)

rect = pysick.graphics.Rect(50, 50, 200, 100, fill=(0, 0, 255))

pysick.graphics.fill_screen((255, 255, 0))
pysick.graphics.draw(rect)

pysick.keys.init()

def loop():
    if pysick.keys.is_pressed(pysick.keys.KEY_LEFT):
        rect.x -= 10
    if pysick.keys.is_pressed(pysick.keys.KEY_RIGHT):
        rect.x += 10
    if pysick.keys.is_pressed(pysick.keys.KEY_UP):
        rect.y -= 10
    if pysick.keys.is_pressed(pysick.keys.KEY_DOWN):
        rect.y += 10

    pysick.graphics.fill_screen((255, 255, 0))
    pysick.graphics.draw(rect)

    pysick.ingine.time_in(30, loop)

loop()
pysick.ingine.run()
```

---

## Drawing Shapes

All fills **must use RGB or RGBA tuples** like `(255, 0, 0)` or `(0, 255, 0, 128)`.

### Rectangle

```python
rect = pysick.graphics.Rect(
    x=100,
    y=50,
    width=200,
    height=100,
    fill=(255, 0, 0)  # red
)
pysick.graphics.draw(rect)
```

### Oval

```python
oval = pysick.graphics.Oval(
    x=150,
    y=100,
    width=100,
    height=60,
    fill=(128, 0, 128, 200)  # semi-transparent purple
)
pysick.graphics.draw(oval)
```

### Circle

```python
circle = pysick.graphics.Circle(
    x=300,
    y=300,
    radius=50,
    fill=(0, 255, 255)
)
pysick.graphics.draw(circle)
```

### Line

```python
line = pysick.graphics.Line(
    x1=50,
    y1=50,
    x2=200,
    y2=200,
    fill=(0, 0, 0)
)
pysick.graphics.draw(line)
```

---

## Fill the Canvas

```python
pysick.graphics.fill_screen((0, 255, 0))  # Green
```

---

## Collision Detection

```python
r1 = pysick.graphics.Rect(10, 10, 50, 50, fill=(255, 0, 0))
r2 = pysick.graphics.Rect(30, 30, 60, 60, fill=(0, 0, 255))

if pysick.colliCheck.rectxrect(r1, r2):
    print("Rectangles overlap!")
```

```python
c1 = pysick.graphics.Circle(100, 100, 30, fill=(0, 255, 0))
c2 = pysick.graphics.Circle(120, 120, 30, fill=(255, 255, 0))

if pysick.colliCheck.circlexcircle(c1, c2):
    print("Circles overlap!")
```

```python
rect = pysick.graphics.Rect(50, 50, 80, 80, fill=(255, 192, 203))
circle = pysick.graphics.Circle(90, 90, 30, fill=(128, 0, 128))

if pysick.colliCheck.rectxcircle(rect, circle):
    print("Rectangle and circle collide!")
```

---

## Displaying Images

```python
pysick.image.show("my_image.png", x=0, y=0)
```

---

## Playing Videos

```python
pysick.image.play(
    video_path="video.mp4",
    resolution=(640, 480),
    fps=24,
    cleanup=True
)
```

---

## Keyboard Input

```python
pysick.keys.init()

def loop():
    if pysick.keys.is_pressed(pysick.keys.KEY_W):
        print("W is held")
    pysick.ingine.time_in(30, loop)

loop()
pysick.ingine.run()
```

---

## About

```python
pysick.about()
```

