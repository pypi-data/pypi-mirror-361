import contextlib
import math
from typing import Sequence, Tuple, Union

from IPython.display import display

from .turtle import DimPoint, Turtle

_turtle = None

# The simplified API.


def _check_turtle():
    global _turtle
    if _turtle is None:
        _turtle = Turtle()
        _turtle.stats = {
            "moves": 0,
            "jumps": 0,
            "strokes": 0,
            "turns": 0,
            "distance": 0,
            "words": [],
            "_in_stroke": False,
        }
        display(_turtle)
    return _turtle


def clear() -> None:
    """Clear the canvas."""
    tu = _check_turtle()
    _turtle.stats = {
        "moves": 0,
        "jumps": 0,
        "strokes": 0,
        "turns": 0,
        "distance": 0,
        "words": [],
        "_in_stroke": False,
    }
    tu.clear()


def move(distance: float) -> None:
    """Move the turtle by distance pixels."""
    tu = _check_turtle()
    tu.stats["moves"] += 1
    if tu._pendown:
        tu.stats["distance"] += abs(distance)
        if not tu.stats["_in_stroke"]:
            tu.stats["strokes"] += 1
            tu.stats["_in_stroke"] += True
    tu.move(distance)


def turn(degrees: float) -> None:
    """Turn the pen by degrees. Positive numbers turn left, negative numbers
    turn right."""
    tu = _check_turtle()
    tu.stats["turns"] += 1
    tu.turn(degrees)


def pen_up() -> None:
    """Pick the pen up. Movements won't make lines."""
    tu = _check_turtle()
    tu.stats["_in_stroke"] = False
    tu.pen_up()


def pen_down() -> None:
    """Put the pen down. Movements will make lines."""
    tu = _check_turtle()
    tu.pen_down()


def show_turtle() -> None:
    """Show the turtle in the scene."""
    tu = _check_turtle()
    tu.show()


def hide_turtle() -> None:
    """Hide the turtle in the scene."""
    tu = _check_turtle()
    tu.hide()


def write(
    text: str, font: str = "24px sans-serif", text_align: str = "center"
) -> None:
    """Write text.

    Arguments:

        text: The text to write
        font: The HTML font specification
        text_align: The alignment of the text relative to the turtle
    """
    tu = _check_turtle()
    tu.stats["words"].append(text)
    tu.write(text, font, text_align)


def goto(x: int, y: int) -> None:
    """Jump to a point"""
    tu = _check_turtle()
    tu.stats["moves"] += 1
    tu.stats["jumps"] += 1
    if tu._pendown:
        distance = math.sqrt((tu.pos[0] - x) ** 2 + (tu.pos[1] - y) ** 2)
        tu.stats["distance"] += distance
        if not tu.stats["_in_stroke"]:
            tu.stats["strokes"] += 1
            tu.stats["_in_stroke"] += True
    tu.pos = (x, y)


def set_background(filename: str) -> None:
    """Set the background image"""
    tu = _check_turtle()
    tu.background(filename)


def set_heading(heading: float) -> None:
    """Set the pen to face heading in degrees."""
    tu = _check_turtle()
    tu.stats["turns"] += 1
    tu.heading = heading


def set_color(color: Union[str, int]) -> None:
    """Set the pen color using HTML color notation."""
    tu = _check_turtle()
    tu.color = color


def set_width(width: int) -> None:
    """Set the line thickness."""
    tu = _check_turtle()
    tu.width = width


def set_size(width: int, height: int) -> None:
    """Set the size of the arena."""
    tu = _check_turtle()
    tu.size = (width, height)


@contextlib.contextmanager
def polygon(
    *,
    color: str | None = None,
    width: int | None = None,
    fill: str | None = None,
):
    """
    Draw a polygon by connecting moves together.

    Example:

    with tu.polygon():
        tu.move(30)
        tu.turn(45)
        tu.move(30)
        tu.turn(45)
        tu.move(30)
    """
    tu = _check_turtle()
    old_color = tu.color
    old_width = tu.width
    old_fill = tu.fill
    try:
        if color is not None:
            tu.color = color
        if fill is not None:
            tu.fill = fill
        if width is not None:
            tu.width = width

        with tu.polygon():
            yield

    finally:
        tu.color = old_color
        tu.fill = old_fill
        tu.width = old_width


def pre_run_cell(info):
    """
    Callback before a cell is run.
    """
    global _turtle
    _turtle = None


def post_run_cell(result):
    """
    Callback after a cell has run.
    """
    global _turtle
    result.turtle = _turtle


def load_ipython_extension(ipython):
    ipython.events.register("pre_run_cell", pre_run_cell)
    ipython.events.register("post_run_cell", post_run_cell)
