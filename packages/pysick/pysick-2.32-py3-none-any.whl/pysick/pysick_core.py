"""pysick.py

PySick - An Bypass for learning Graphics Development

Classes:
    SickError - Custom error for PySick
    InGine - Main engine/window class
    graphics - Drawing utility class
    message_box - Messagebox utilities
"""


from . import _tkinter_pysick as tk
from . import _messagebox_pysick as messagebox

def _color_to_hex(color):
    """
    Convert (R,G,B) or (R,G,B,A) tuple to #RRGGBB hex string for tkinter.

    Args:
        color: A string (e.g. "red") or tuple like (R, G, B) or (R, G, B, A).

    Returns:
        A tkinter-compatible color string like "#ff00cc".
    """
    if isinstance(color, tuple):
        if len(color) == 3:
            r, g, b = color
        elif len(color) == 4:
            r, g, b, _ = color  # Ignore alpha for now
        else:
            raise ValueError("Color tuple must be RGB or RGBA.")
        return f'#{r:02x}{g:02x}{b:02x}'
    elif isinstance(color, str):
        return color  # Already a color name or hex
    else:
        raise ValueError("Color must be a tuple or a string.")


SickVersion = "2.32"


try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
except Exception:
    try:
        windll.user32.SetProcessDPIAware()    # Windows Vista+
    except Exception:
        pass


class SickError(Exception):
    """
    Custom error for PySick module.

    Parameters:
        message (str): Optional error message.
    """

    def __init__(self, message="A SickError occurred!"):
        super().__init__(message)


class ingine:
    """
    PySick InGine class for managing the Tkinter window and canvas.

    Parameters:
        width (int): Window width in pixels.
        height (int): Window height in pixels.
    """

    _root = None
    _canvas = None
    width = 0
    height = 0

    @classmethod
    def init(cls, width, height):
        """
        Initialize the engine window and canvas.
        """
        print(f"[pysick] Window Initialized with {width}x{height}")

        cls._root = tk.Tk()
        cls._root.title("pysick graphics")

        cls.width = width
        cls.height = height
        cls._root.geometry(f"{width}x{height}")

        cls._canvas = tk.Canvas(cls._root, width=width, height=height)
        cls._canvas.pack()

        try:
            import os
            import sys
            py_icon_path = os.path.join(os.path.dirname(sys.executable), 'DLLs', 'pyc.ico')
            try:
                cls._root.iconbitmap(py_icon_path)
            except Exception:
                pass
        except Exception as ex:
            raise SickError(str(ex))

    @classmethod
    def _get_canvas(cls):
        import inspect
        caller = inspect.stack()[1].frame.f_globals["__name__"]
        if not caller.startswith("pysick."):
            raise SickError(f"Unauthorized access from {caller}")
        return cls._canvas

    @classmethod
    def run(cls):
        """
        Run the Tkinter main loop.
        """
        cls._root.mainloop()

    @classmethod
    def set_title(cls, title):
        """
        Set the window title.

        Parameters:
            title (str): New title for the window.
        """
        cls._root.title(title)



    @classmethod
    def add_label(cls, text, x, y, font=("Arial", 14), color="black"):
        """
        Add a text label to the window.
        """
        label = tk.Label(cls._root, text=text, font=font, fg=color)
        label.place(x=x, y=y)
        return label

    @classmethod
    def add_button(cls, text, x, y, func, width=10, height=2):
        """
        Add a clickable button.
        """
        button = tk.Button(
            cls._root,
            text=text,
            command=func,
            width=width,
            height=height
        )
        button.place(x=x, y=y)
        return button

    @classmethod
    def time_in(cls, ms, func):
        """
        Schedule a function to run after a delay.
        """
        cls._root.after(ms, func)

    @classmethod
    def quit(cls):
        """
        Destroy the window and quit the program.
        """
        cls._root.destroy()

class graphics:
    """
    PySick drawing utilities for shapes and screen manipulation.
    """

    class Rect:
        """
        Rectangle shape.
        """
        def __init__(self, x, y, width, height, fill):
            self._shape_type = "rect"
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.fill = fill

    class Oval:
        """
        Oval shape.
        """
        def __init__(self, x, y, width, height, fill):
            self._shape_type = "oval"
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.fill = fill

    class Circle:
        """
        Circle shape.
        """
        def __init__(self, x, y, radius, fill):
            self._shape_type = "circle"
            self.x = x
            self.y = y
            self.radius = radius
            self.fill = fill

    class Line:
        """
        Line shape.
        """
        def __init__(self, x1, y1, x2, y2, fill):
            self._shape_type = "line"
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.fill = fill


    @staticmethod
    def fill_screen( fill):
        """
        Fill the entire screen with a solid color.
        """
        master = ingine
        canvas = master._get_canvas()
        canvas.delete("all")
        fill_color = _color_to_hex(fill)
        canvas.create_rectangle(
            0, 0,
            master.width,
            master.height,
            fill=fill_color
        )

    @staticmethod
    def draw( shape):
        """
        Draw any shape object.

        Parameters:
            master (InGine): The engine window.
            shape: A shape instance from graphics class.
        """
        master = ingine
        canvas = master._get_canvas()

        try:
            shape_type = getattr(shape, "_shape_type", None)

            fill_color = _color_to_hex(shape.fill)

            if shape_type == "rect":
                x2 = shape.x + shape.width
                y2 = shape.y + shape.height
                canvas.create_rectangle(shape.x, shape.y, x2, y2, fill=fill_color)

            elif shape_type == "oval":
                x2 = shape.x + shape.width
                y2 = shape.y + shape.height
                canvas.create_oval(shape.x, shape.y, x2, y2, fill=fill_color)

            elif shape_type == "circle":
                r = shape.radius
                canvas.create_oval(
                    shape.x - r,
                    shape.y - r,
                    shape.x + r,
                    shape.y + r,
                    fill=fill_color
                )

            elif shape_type == "line":
                canvas.create_line(
                    shape.x1, shape.y1,
                    shape.x2, shape.y2,
                    fill=fill_color
                )

            else:
                raise SickError("Invalid shape object passed to graphics.draw().")

        except Exception as ex:
            raise SickError(str(ex))

    @staticmethod
    def draw_polygon(points, fill, master=None):
        """
        Draw a polygon shape.

        Parameters:
            points (list of tuples): [(x1, y1), (x2, y2), ...]
            fill (str or tuple): Color
            master (InGine): Optional engine instance.
        """
        canvas = master._get_canvas() if master else ingine._get_canvas()
        fill = _color_to_hex(fill)
        coords = []
        for x, y in points:
            coords.extend([x, y])
        canvas.create_polygon(coords, fill=fill)

    @staticmethod
    def draw_text(x, y, text, font=("Arial", 16), fill=(0, 0, 0), anchor="nw", master=None):
        """
        Draw text on the canvas.

        Parameters:
            x (int)
            y (int)
            text (str)
            font (tuple)
            fill (str or tuple)
            anchor (str)
            master (InGine)
        """
        canvas = master._get_canvas() if master else ingine._get_canvas()
        fill = _color_to_hex(fill)
        canvas.create_text(x, y, text=text, font=font, fill=fill, anchor=anchor)


class message_box:
    """
    PySick messagebox utility class.
    """

    @staticmethod
    def ask_question(title, text):
        """
        Show a question dialog.

        Parameters:
            title (str)
            text (str)
        """
        return messagebox.askquestion(title, text)


    @staticmethod
    def show_info(title, text):
        """
        Show an informational dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showinfo(title, text)


    @staticmethod
    def show_warning(title, text):
        """
        Show a warning dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showwarning(title, text)


    @staticmethod
    def show_error(title, text):
        """
        Show an error dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showerror(title, text)


    @staticmethod
    def about(title, text):
        """
        Show an about dialog.

        Parameters:
            title (str)
            text (str)
        """
        messagebox.showinfo(title, text)


def about():
    """
    Show PySick about messagebox.

    Parameters:
        -
    """
    messagebox.showinfo(
        "pysick shows: messagebox.about()",
        f"Hello, this is pysick(v.{SickVersion}), tk(-v{str(tk.TkVersion)}), Tcl(v-3.10)"
    )

class image:

    @staticmethod
    def extract_frames(video_path, output_folder, size):

        import os

        os.makedirs(output_folder, exist_ok=True)
        w, h = size
        cmd = f'ffmpeg -i "{video_path}" -vf scale={w}:{h} "{output_folder}/frame_%04d.png"'
        os.system(cmd)

    @staticmethod
    def cleanup_frames(folder):

        import os

        for f in os.listdir(folder):

            os.remove(os.path.join(folder, f))

        os.rmdir(folder)


    @staticmethod
    def play(video_path, resolution=(320, 240), fps=24, cleanup=True):

        """
        Public method to play a video on a given engine (InGine instance).

        Parameters:
            video_path  : Path to video file (.mp4)
            resolution  : Tuple (width, height)
            fps         : Frames per second
            cleanup     : Whether to delete frames after playback
        """
        import os

        engine = ingine
        canvas = engine._canvas

        _root = canvas.winfo_toplevel()

        frame_folder = "_video_frames"

        video_path = os.path.abspath(video_path)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"[pysick.video] Video not found: {video_path}")

        image.extract_frames(video_path, frame_folder, resolution)

        frames = sorted(f for f in os.listdir(frame_folder) if f.endswith(".png"))

        if not frames:
            raise RuntimeError("[pysick.video] No frames extracted. ffmpeg may have failed.")

        index = 0

        tk_img = tk.PhotoImage(file=os.path.join(frame_folder, frames[0]))
        img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)

        def advance():

            nonlocal index, tk_img

            if index < len(frames):

                frame_path = os.path.join(frame_folder, frames[index])
                tk_img = tk.PhotoImage(file=frame_path)

                canvas.itemconfig(img_id, image=tk_img)
                canvas.image = tk_img  # avoid garbage collection

                index += 1

                _root.after(int(1000 / fps), advance)

            else:

                if cleanup:
                    image.cleanup_frames(frame_folder)

                print("[pysick.video] Video playback finished.")

        advance()

    @staticmethod
    def show(engine, image_path, x=0, y=0, anchor="nw"):
        """
        Displays an image on the engine's canvas.

        Parameters:
            engine     : InGine instance from pysick
            image_path : Path to the image file (.png, .jpg, etc.)
            x       : Position on canvas
            y       : Position on the canvas
            anchor     : Anchor point (default: "nw" = top-left)
        """

        import os

        if not os.path.exists(image_path):

            raise FileNotFoundError(f"[pysick.photo] Image file not found: {image_path}")

        img = tk.PhotoImage(file=image_path)

        engine._canvas.create_image(x, y, image=img, anchor=anchor)
        engine._canvas.image = img  # prevent garbage collection

        print(f"[pysick.photo] Displayed: {image_path}")

class colliCheck:
    """
    PySick collision checking utilities.
    """

    @staticmethod
    def rectxrect(one_rect, another_rect):
        """
        Check if two rectangles collide.

        Parameters:
            one_rect (graphics.Rect)
            another_rect (graphics.Rect)

        Returns:
            bool
        """
        return (
            one_rect.x < another_rect.x + another_rect.width and
            one_rect.x + one_rect.width > another_rect.x and
            one_rect.y < another_rect.y + another_rect.height and
            one_rect.y + one_rect.height > another_rect.y
        )


    @staticmethod
    def circlexcircle(one_circle, another_circle):
        """
        Check if two circles collide.

        Parameters:
            one_circle (graphics.Circle)
            another_circle (graphics.Circle)

        Returns:
            bool
        """
        dx = another_circle.x - one_circle.x
        dy = another_circle.y - one_circle.y
        distance_squared = dx * dx + dy * dy
        radius_sum = one_circle.radius + another_circle.radius

        return distance_squared < radius_sum * radius_sum


    @staticmethod
    def rectxcircle(rect, circle):
        """
        Check if a rectangle and a circle collide.

        Parameters:
            rect (graphics.Rect)
            circle (graphics.Circle)

        Returns:
            bool
        """
        # Find the closest point on the rect to the circle center
        closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
        closest_y = max(rect.y, min(circle.y, rect.y + rect.height))

        dx = circle.x - closest_x
        dy = circle.y - closest_y

        return (dx * dx + dy * dy) < (circle.radius * circle.radius)

class keys:
    """
    PySick keys input handler.

    Usage:
        keys.init()
        if keys.KEY_W:
            # do something
    """

    # Class-level dictionary to track key states
    __state = {}

    # Mapping from readable constants → actual characters
    # Letters
    KEY_A = "A"
    KEY_B = "B"
    KEY_C = "C"
    KEY_D = "D"
    KEY_E = "E"
    KEY_F = "F"
    KEY_G = "G"
    KEY_H = "H"
    KEY_I = "I"
    KEY_J = "J"
    KEY_K = "K"
    KEY_L = "L"
    KEY_M = "M"
    KEY_N = "N"
    KEY_O = "O"
    KEY_P = "P"
    KEY_Q = "Q"
    KEY_R = "R"
    KEY_S = "S"
    KEY_T = "T"
    KEY_U = "U"
    KEY_V = "V"
    KEY_W = "W"
    KEY_X = "X"
    KEY_Y = "Y"
    KEY_Z = "Z"

    # Digits
    KEY_0 = "0"
    KEY_1 = "1"
    KEY_2 = "2"
    KEY_3 = "3"
    KEY_4 = "4"
    KEY_5 = "5"
    KEY_6 = "6"
    KEY_7 = "7"
    KEY_8 = "8"
    KEY_9 = "9"

    # Arrow keys
    KEY_LEFT = "Left"
    KEY_RIGHT = "Right"
    KEY_UP = "Up"
    KEY_DOWN = "Down"

    # Modifier keys
    KEY_SHIFT_L = "Shift_L"
    KEY_SHIFT_R = "Shift_R"
    KEY_CONTROL_L = "Control_L"
    KEY_CONTROL_R = "Control_R"
    KEY_ALT_L = "Alt_L"
    KEY_ALT_R = "Alt_R"
    KEY_CAPS_LOCK = "Caps_Lock"

    # Space and enter
    KEY_SPACE = "space"
    KEY_RETURN = "Return"
    KEY_TAB = "Tab"
    KEY_BACKSPACE = "BackSpace"
    KEY_ESCAPE = "Escape"

    # Symbols / punctuation
    KEY_EXCLAMATION = "exclam"
    KEY_AT = "at"
    KEY_HASH = "numbersign"
    KEY_DOLLAR = "dollar"
    KEY_PERCENT = "percent"
    KEY_CARET = "asciicircum"
    KEY_AMPERSAND = "ampersand"
    KEY_ASTERISK = "asterisk"
    KEY_LEFT_PAREN = "parenleft"
    KEY_RIGHT_PAREN = "parenright"
    KEY_MINUS = "minus"
    KEY_UNDERSCORE = "underscore"
    KEY_EQUALS = "equal"
    KEY_PLUS = "plus"
    KEY_LEFT_BRACE = "braceleft"
    KEY_RIGHT_BRACE = "braceright"
    KEY_LEFT_BRACKET = "bracketleft"
    KEY_RIGHT_BRACKET = "bracketright"
    KEY_SEMICOLON = "semicolon"
    KEY_COLON = "colon"
    KEY_QUOTE = "quoteright"
    KEY_DOUBLE_QUOTE = "quotedbl"
    KEY_COMMA = "comma"
    KEY_PERIOD = "period"
    KEY_SLASH = "slash"
    KEY_BACKSLASH = "backslash"
    KEY_PIPE = "bar"
    KEY_LESS = "less"
    KEY_GREATER = "greater"
    KEY_QUESTION = "question"

    # Function keys
    KEY_F1 = "F1"
    KEY_F2 = "F2"
    KEY_F3 = "F3"
    KEY_F4 = "F4"
    KEY_F5 = "F5"
    KEY_F6 = "F6"
    KEY_F7 = "F7"
    KEY_F8 = "F8"
    KEY_F9 = "F9"
    KEY_F10 = "F10"
    KEY_F11 = "F11"
    KEY_F12 = "F12"

    # --- Internal storage ---
    _pressed = {}
    _pressed_once = set()

    @staticmethod
    def init():
        """
        Initialize key tracking on the Tk root window.
        Should be called AFTER pysick.ingine.init().
        """
        from pysick import ingine

        root = ingine._root

        def on_press(event):
            k = keys._normalize(event.keysym)
            keys._pressed[k] = True

        def on_release(event):
            k = keys._normalize(event.keysym)
            if keys._pressed.get(k, False):
                keys._pressed_once.add(k)
            keys._pressed[k] = False

        root.bind("<KeyPress>", on_press)
        root.bind("<KeyRelease>", on_release)

    @staticmethod
    def is_pressed(key):
        """
        Check if the given key is currently held down.

        Parameters:
            key (str): One of the key constants above.

        Returns:
            bool: True if held down, else False.
        """
        return keys._pressed.get(key, False)

    @staticmethod
    def was_pressed(key):
        """
        Check if the given key was pressed and released since last check.
        Good for one-shot triggers.

        Parameters:
            key (str)

        Returns:
            bool
        """
        if key in keys._pressed_once:
            keys._pressed_once.remove(key)
            return True
        return False

    @staticmethod
    def _normalize(name):
        """
        Normalize key names for consistent dictionary lookup.
        """
        return name.upper() if len(name) == 1 else name

# pysick/mouse.py

class mouse:
    """
    PySick Mouse Input Handler
    """

    # Internal state
    _buttons = {
        "LEFT": False,
        "MIDDLE": False,
        "RIGHT": False,
    }

    LEFT = "LEFT"
    MIDDLE = "MIDDLE"
    RIGHT = "RIGHT"

    _position = (0, 0)
    _wheel_delta = 0

    @staticmethod
    def init():
        """
        Initialize mouse bindings.
        Should be called once after creating the window.
        """
        root = ingine._root

        # Mouse button events
        root.bind("<ButtonPress-1>", lambda e: mouse._set_button("LEFT", True))
        root.bind("<ButtonRelease-1>", lambda e: mouse._set_button("LEFT", False))

        root.bind("<ButtonPress-2>", lambda e: mouse._set_button("MIDDLE", True))
        root.bind("<ButtonRelease-2>", lambda e: mouse._set_button("MIDDLE", False))

        root.bind("<ButtonPress-3>", lambda e: mouse._set_button("RIGHT", True))
        root.bind("<ButtonRelease-3>", lambda e: mouse._set_button("RIGHT", False))

        # Mouse motion
        root.bind("<Motion>", mouse._on_motion)

        # Mouse wheel
        root.bind("<MouseWheel>", mouse._on_wheel)

    @staticmethod
    def _set_button(button, state):
        mouse._buttons[button] = state

    @staticmethod
    def _on_motion(event):
        mouse._position = (event.x, event.y)

    @staticmethod
    def _on_wheel(event):
        mouse._wheel_delta = event.delta

    @staticmethod
    def is_pressed(button):
        """
        Check if a mouse button is pressed.

        Parameters:
            button (str): "LEFT", "MIDDLE", or "RIGHT"

        Returns:
            bool
        """
        return mouse._buttons.get(button, False)

    @staticmethod
    def get_pos():
        """
        Get current mouse position.

        Returns:
            (x, y) tuple
        """
        return mouse._position

    @staticmethod
    def get_wheel_delta():
        """
        Get last wheel delta.

        Returns:
            int
        """
        return mouse._wheel_delta
class gui:
    """
    PySick GUI class with static methods for adding widgets
    to the ingine window.
    """

    _widgets = []

    @staticmethod
    def add_label(text, x, y, font=("Arial", 14), color="black"):
        root = ingine._root
        label = tk.Label(root, text=text, font=font, fg=color)
        label.place(x=x, y=y)
        gui._widgets.append(label)
        return label

    @staticmethod
    def add_button(text, x, y, func, width=10, height=2):
        root = ingine._root
        button = tk.Button(root, text=text, command=func, width=width, height=height)
        button.place(x=x, y=y)
        gui._widgets.append(button)
        return button

    @staticmethod
    def add_entry(x, y, width=20):
        root = ingine._root
        entry = tk.Entry(root, width=width)
        entry.place(x=x, y=y)
        gui._widgets.append(entry)
        return entry

    @staticmethod
    def add_checkbutton(text, x, y, variable=None):
        """
        Add a checkbox.

        Parameters:
            text (str): Label text.
            x, y (int): Position.
            variable (tk.BooleanVar): Optional external variable.

        Returns:
            tk.Checkbutton, tk.BooleanVar
        """
        root = ingine._root
        var = variable or tk.BooleanVar()
        check = tk.Checkbutton(root, text=text, variable=var)
        check.place(x=x, y=y)
        gui._widgets.append(check)
        return check, var

    @staticmethod
    def add_radiobutton(text, x, y, variable, value):
        """
        Add a radiobutton.

        Parameters:
            text (str): Button text.
            x, y (int): Position.
            variable (tk.Variable): The shared variable for all radio buttons.
            value (any): The value assigned if selected.

        Returns:
            tk.Radiobutton
        """
        root = ingine._root
        radio = tk.Radiobutton(root, text=text, variable=variable, value=value)
        radio.place(x=x, y=y)
        gui._widgets.append(radio)
        return radio

    @staticmethod
    def add_scale(x, y, from_=0, to=100, orient='horizontal', length=200):
        """
        Add a slider (scale).

        Parameters:
            x, y (int): Position.
            from_, to (int): Min and max values.
            orient (str): 'horizontal' or 'vertical'.
            length (int): Pixel length.

        Returns:
            tk.Scale
        """
        root = ingine._root
        scale = tk.Scale(root, from_=from_, to=to, orient=orient, length=length)
        scale.place(x=x, y=y)
        gui._widgets.append(scale)
        return scale

    @staticmethod
    def add_textbox(x, y, width=40, height=5):
        """
        Add a multi-line text box.

        Parameters:
            x, y (int): Position.
            width (int): Character width.
            height (int): Number of lines.

        Returns:
            tk.Text
        """
        root = ingine._root
        textbox = tk.Text(root, width=width, height=height)
        textbox.place(x=x, y=y)
        gui._widgets.append(textbox)
        return textbox

    @staticmethod
    def clear():
        """
        Destroy all widgets created via gui class.
        """
        for widget in gui._widgets:
            widget.destroy()
        gui._widgets.clear()


if __name__ != "__main__":
    print(f"--------------------pysick (v.{SickVersion},2.1.2026), tk(-v{tk.TkVersion}), Tcl(v-3.10) ShellRelease-------------------------")