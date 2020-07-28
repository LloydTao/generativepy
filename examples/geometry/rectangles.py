from generativepy.drawing import make_image, setup
from generativepy.color import Color
from generativepy.geometry import Rectangle, rectangle


def draw(ctx, width, height, frame_no, frame_count):
    setup(ctx, width, height, width=5, background=Color(0.8))

    rectangle(ctx, 1, 1, 1, 1)
    ctx.set_source_rgba(*Color(1, 0, 0))
    ctx.fill()

    Rectangle(ctx).of_corner_size(3, 1, 1, 1).fill(Color(0, .5, 0))
    Rectangle(ctx).of_corner_size(1, 3, 1, 1).stroke(Color(0, .5, 0), 0.1)
    Rectangle(ctx).of_corner_size(3, 3, 1, 1).fill_stroke(Color(0, 0, 1), Color(0), 0.2)

make_image("/tmp/geometry-rectangles.png", draw, 500, 500)
