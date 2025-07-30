# PySick - Getting Started

PySick is a simple graphics library built on top of Tkinter.  
It makes creating shapes, windows, input handling, and basic games super easy!

---

## Getting Started

Here’s how to open a window, draw a rectangle, and start the main loop.

```python
import pysick

# Create a window (800 x 600 pixels)
pysick.ingine.init(800, 600)

# Create a rectangle shape
rect = pysick.graphics.Rect(
    x=100,
    y=100,
    width=200,
    height=100,
    fill=(255, 0, 0)  # Red color
)

# Fill the entire screen with dark gray
pysick.graphics.fill_screen((30, 30, 30))

# Draw the rectangle shape
pysick.graphics.draw(rect)

# Start the main loop
pysick.ingine.run()
```

---

## Running Without mainloop()

PySick can also work in a `while` loop for more game-like programs:

```python
import pysick

pysick.ingine.init(800, 600)

rect = pysick.graphics.Rect(100, 100, 200, 100, fill=(0, 255, 0))

while not pysick.QUIT:
    pysick.graphics.fill_screen((0, 0, 0))
    pysick.graphics.draw(rect)
    pysick.ingine.slap()
```

---

## Colors

You can use:

- Named colors, like `"red"`
- RGB tuples, like `(255, 0, 0)`
- RGBA tuples (alpha is ignored in Tkinter)

Example:

```python
rect = pysick.graphics.Rect(
    x=50,
    y=50,
    width=100,
    height=50,
    fill="blue"
)
```

Or with RGB:

```python
rect = pysick.graphics.Rect(
    x=50,
    y=50,
    width=100,
    height=50,
    fill=(0, 128, 255)
)
```

---

## Shapes

PySick supports:

- Rectangle
- Oval
- Circle
- Line
- Polygon
- Text

Example:

```python
oval = pysick.graphics.Oval(200, 150, 80, 40, fill="purple")
pysick.graphics.draw(oval)

line = pysick.graphics.Line(50, 50, 200, 200, fill=(255, 255, 0))
pysick.graphics.draw(line)

polygon_points = [(50, 50), (100, 150), (150, 50)]
pysick.graphics.draw_polygon(polygon_points, fill=(0, 255, 255))

text = "Hello, PySick!"
pysick.graphics.draw_text(300, 300, text, fill=(255, 255, 255))
```

---

## Input Handling

### Keyboard

```python
pysick.keys.init()

if pysick.keys.is_pressed(pysick.keys.KEY_LEFT):
    print("Left arrow is held!")

if pysick.keys.was_pressed(pysick.keys.KEY_SPACE):
    print("Space was pressed!")
```

---

### Mouse

```python
pysick.mouse.init()

if pysick.mouse.is_pressed(pysick.mouse.LEFT):
    print("Left mouse button pressed.")

x, y = pysick.mouse.get_pos()
print(f"Mouse is at {x},{y}")
```

---

## GUI Widgets

```python
pysick.gui.add_label("Hello!", 100, 100)
pysick.gui.add_button("Click Me", 200, 200, lambda: print("Clicked!"))
entry = pysick.gui.add_entry(300, 300)

# Checkbuttons and radiobuttons:
check, var = pysick.gui.add_checkbutton("Enable", 400, 400)
radio_var = tk.StringVar()
radio = pysick.gui.add_radiobutton("Option A", 500, 500, radio_var, value="A")
```

---

## Videos and Images

Show an image:

```python
pysick.image.show(pysick.ingine, "my_picture.png")
```

Play a video:

```python
pysick.image.play("my_video.mp4")
```

---

## Ticking

Replace time.sleep() with pysick’s tick helper:

```python
pysick.tick(16)   # wait ~16ms
```

---

## QUIT Flag

Inside your while-loop game:

```python
while not pysick.QUIT:
    # game logic
    pysick.ingine.slap()
```

---

## About

```python
pysick.about()
```

Displays PySick version info.

---

That’s it — you’re ready to build cool stuff!


