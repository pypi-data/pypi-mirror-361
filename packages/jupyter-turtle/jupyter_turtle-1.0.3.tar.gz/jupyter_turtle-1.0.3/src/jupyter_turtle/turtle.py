"""
A simple implementation of turtle graphics for teaching algorithms.

Author: Mike Matera
"""

import colorsys
import contextlib
import math
import pathlib
from collections import namedtuple
from collections.abc import Sequence

import numpy
import PIL
from ipycanvas import Canvas, MultiCanvas, hold_canvas
from IPython.display import display

DimPoint = namedtuple("DimPoint", ["x", "y"])


class Turtle:
    def __init__(self, size: tuple[int, int] = (600, 300), **kwargs):
        """Create a Turtle drawing canvas.

        Arguments:
            size: Set the size of the canvas.
        """
        # Load the Turtle image
        turtle = numpy.array(
            PIL.Image.open(pathlib.Path(__file__).parent / "turtle.png")
        )
        self._turtle = Canvas(width=turtle.shape[0], height=turtle.shape[1])
        self._turtle.put_image_data(turtle)

        # Create a new Canvas
        self._size = DimPoint(size[0], size[1])
        self._canvas = MultiCanvas(
            n_canvases=3,
            width=self._size.x,
            height=self._size.y,
            sync_image_data=True,
            **kwargs,
        )

        # Initialize properties
        self._current = self._to_native(DimPoint(0, 0))
        self._cur_heading = (3 * math.pi) / 2  # in Canvas Y is negative.
        self._pendown = True
        self._show = True
        self._fill = None
        self._image = None
        self._polygon = False

        # Render the turtle
        with self._do_draw():
            self._canvas.clear()

    @contextlib.contextmanager
    def _do_draw(self):
        """Context manager that combines all drawing operations and re-renders
        the turtle."""
        with hold_canvas(self._canvas):
            yield
            self._canvas[2].clear()
            if self._show:
                # Redraw the Turtle
                self._canvas[2].save()
                self._canvas[2].translate(self._current.x, self._current.y)
                self._canvas[2].rotate(self._cur_heading + math.pi / 2)
                self._canvas[2].draw_image(
                    self._turtle, x=-15, y=-15, width=30, height=30
                )
                self._canvas[2].restore()

    def _to_native(self, point: tuple[int, int]) -> DimPoint:
        """Convert Turtle coordinates to native ones."""
        return DimPoint(
            x=self._size.x // 2 + point[0], y=self._size.y // 2 - point[1]
        )

    def _to_turtle(self, point: DimPoint) -> tuple[int, int]:
        """Convert Turtle coordinates to native ones."""
        return (point[0] - self._size.x // 2, self._size.y // 2 - point[1])

    def _ipython_display_(self):
        display(self._canvas)

    def _move(self, to: DimPoint):
        """Low-level move operation."""
        start = self._current
        self._current = to
        with self._do_draw():
            if self._polygon:
                if self._pendown:
                    self._canvas[1].line_to(*self._current)
                else:
                    self._canvas[1].move_to(*start)
            else:
                if self._pendown:
                    self._canvas[1].begin_path()
                    self._canvas[1].move_to(*start)
                    self._canvas[1].line_to(*self._current)
                    self._canvas[1].stroke()

    def clear(self):
        """Clear all drawing."""
        self._canvas[1].clear()

    def move(self, distance: float):
        """Move the turtle by distance pixels."""
        self._move(
            DimPoint(
                x=self._current.x + math.cos(self._cur_heading) * distance,
                y=self._current.y + math.sin(self._cur_heading) * distance,
            )
        )

    def turn(self, degrees: float):
        """Turn the pen by degrees."""
        with self._do_draw():
            self._cur_heading = (self._cur_heading - math.radians(degrees)) % (
                math.pi * 2
            )

    def pen_up(self):
        """Pick the pen up. Movements won't make lines."""
        self._pendown = False

    def pen_down(self):
        """Put the pen down. Movements will make lines."""
        self._pendown = True

    def show(self):
        """Show the turtle in the scene."""
        with self._do_draw():
            self._show = True

    def hide(self):
        """Hide the turtle in the scene."""
        with self._do_draw():
            self._show = False

    def background(self, filename: str):
        """Set the background image"""
        self._image = numpy.array(PIL.Image.open(filename))
        self.size = (self._image.shape[1], self._image.shape[0])
        self._canvas[0].put_image_data(self._image)

    @contextlib.contextmanager
    def polygon(self):
        """Context manager for drawing a polygon."""
        self._polygon = True
        self._canvas[1].begin_path()
        self._canvas[1].move_to(*self._current)
        try:
            yield
        finally:
            self._canvas[1].close_path()
            self._canvas[1].stroke()
            if self._fill is not None:
                self._canvas[1].fill()
            self._polygon = False

    def write(
        self,
        text: str,
        font: str = "24px sans-serif",
        text_align: str = "center",
    ):
        """Write text.

        Arguments:

            text: The text to write
            font: The HTML font specification
            text_align: The alignment of the text relative to the turtle
            line_color: The color of the outline of the text (defaults to the pen color)
            fill_color: The color of the fill of the text (defaults to the pen color)
        """
        with self._do_draw():
            self._canvas[1].translate(self._current.x, self._current.y)
            self._canvas[1].rotate(self._cur_heading + math.pi / 2)
            self._canvas[1].font = font
            self._canvas[1].text_align = text_align
            self._canvas[1].fill_text(text, 0, 0)
            self._canvas[1].stroke_text(text, 0, 0)
            self._canvas[1].reset_transform()

    @property
    def size(self) -> tuple[int, int]:
        """Get the size of the canvas' color buffer (not layout size)."""
        return (self._size.x, self._size.y)

    @size.setter
    def size(self, newsize: tuple[int, int]):
        """Resize the canvas element and adjust they layout size."""
        self._size = DimPoint(x=newsize[0], y=newsize[1])
        with self._do_draw():
            self._canvas.width = self._size.x
            self._canvas.height = self._size.y

            # Move the turtle to the center
            self._current = self._to_native(DimPoint(0, 0))
            self._cur_heading = (3 * math.pi) / 2  # in Canvas Y is negative.

            if self._size.x >= 800:
                self._canvas.layout.width = "90%"
                self._canvas.layout.max_width = f"{self._size.x}px"
                self._canvas.layout.min_width = "800px"
            else:
                self._canvas.layout.width = "auto"
                self._canvas.layout.max_width = "auto"
                self._canvas.layout.min_width = "auto"

    @property
    def pos(self) -> tuple[int, int]:
        """Get the current location of the Turtle."""
        return self._to_turtle(self._current)

    @pos.setter
    def pos(self, *place: tuple[int, int] | Sequence[int] | DimPoint):
        """Goto a point in the coordinate space."""
        if len(place) == 0:
            raise ValueError("Goto where?")
        elif isinstance(place[0], DimPoint):
            p = place[0]
        elif isinstance(place[0], tuple):
            p = DimPoint._make(*place)
        else:
            p = DimPoint._make(place)

        self._move(self._to_native(p))

    @property
    def heading(self) -> float:
        """Get the current heading."""
        return -math.degrees(self._cur_heading + math.pi / 2) % 360

    @heading.setter
    def heading(self, heading: float):
        """Set the pen to face heading in degrees."""
        with self._do_draw():
            self._cur_heading = math.radians(-heading - 90) % (math.pi * 2)

    def _hue_to_html(self, hue: int):
        """Convert a color number from 0 to 365 to HTML"""
        rgb = colorsys.hsv_to_rgb((hue % 365) / 364, 1, 1)
        return f"#{round(rgb[0] * 255):02x}{round(rgb[1] * 255):02x}{round(rgb[2] * 255):02x}"

    @property
    def color(self) -> str:
        """Set the pen color using HTML color notation."""
        return self._canvas[1].stroke_style

    @color.setter
    def color(self, color: str | int):
        """Set the pen color using HTML color notation."""
        if color.__class__ in [int, float]:
            color = self._hue_to_html(color)
        self._canvas[1].stroke_style = color

    @property
    def fill(self) -> str:
        """Set the pen color using HTML color notation."""
        return self._fill

    @fill.setter
    def fill(self, color: str):
        """Set the pen color using HTML color notation."""
        if color.__class__ in [int, float]:
            color = self._hue_to_html(color)
        self._fill = color
        if color is not None:
            self._canvas[1].fill_style = color

    @property
    def width(self) -> int:
        """The line thickness."""
        return self._canvas[1].line_width

    @width.setter
    def width(self, width: int):
        """Set the line thickness."""
        self._canvas[1].line_width = width

    @property
    def image(self) -> PIL.Image:
        """Return an image of the Canvas."""
        return PIL.Image.fromarray(self._image)
