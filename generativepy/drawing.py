# Author:  Martin McBride
# Created: 2018-10-22
# Copyright (C) 2018, Martin McBride
# License: MIT

import cairo
import math
import colorsys

# Color modes
RGB = 1
HLS = 2

#Ellipse and rectangle modes
CENTER = 0
RADIUS = 1
CORNER = 2
CORNERS = 3

#Arc types
OPEN = 0
CHORD = 1
PIE = 2

#Line end
ROUND = 0
SQUARE = 1
PROJECT = 2

#Line join
MITER = 0
BEVEL = 1
ROUND = 2

# Current color mode (global)

gColorMode = RGB


def colorMode(mode):
    global gColorMode
    gColorMode = mode


class Color():

    def __init__(self, *args, mode=0):
        if len(args) == 1:
            self.color = (args[0],)*3
            self.alpha = ()
        elif len(args) == 3:
            self.color = tuple(args)
            self.alpha = ()
        elif len(args) == 4:
            self.color = tuple(args[:3])
            self.alpha = (args[3],)
        else:
            raise ValueError("Color takes 1, 3 or 4 arguments")
        self.mode = mode if mode else gColorMode

    def getRGB(self):
        if self.mode == RGB:
            return self.color + self.alpha
        else:
            return colorsys.hls_to_rgb(*self.color) + self.alpha

    def getHSB(self):
        if self.mode == HSB:
            return self.color + self.alpha
        else:
            return colorsys.rgb_to_hls(*self.color) + self.alpha


def convertMode(mode, a, b, c, d):
    '''
    Convert the parameters a, b, c, d for a rectangle or ellipse based on the mode
    :param mode:
    :param a:
    :param b:
    :param c:
    :param d:
    :return: cx, cy, rx, ry as tuple
    '''
    if mode == RADIUS:
        return a, b, c, d
    elif mode == CENTER:
        return a, b, c / 2, d / 2
    elif mode == CORNERS:
        return (a+c)/2, (b+d)/2, (c-a)/2, (d-b)/2
    else:
        return a+c/2, b+d/2, c/2, d/2


class Canvas:

    def __init__(self, ctx, pixelSize):
        self.pixelSize = pixelSize
        self.ctx = ctx
        self.initial_matrix = ctx.get_matrix()
        self.fillColor = None
        self.strokeColor = (0, 0, 0)
        self.lineWidth = 1
        self.vRectMode = CORNER
        self.vEllipseMode = CENTER
        self.vStrokeJoin = MITER

    def setColor(self, color):
        rgb = color.getRGB()
        if len(rgb) == 4:
            self.ctx.set_source_rgba(*rgb)
        else:
            self.ctx.set_source_rgb(*rgb)

    def fillStroke(self):
        if self.fillColor:
            self.setColor(self.fillColor)
            if self.strokeColor:
                self.ctx.fill_preserve()
            else:
                self.ctx.fill()
        if self.strokeColor:
            self.ctx.set_line_width(self.lineWidth)
            self.setColor(self.strokeColor)
            self.ctx.stroke()

    def scale(self, x, y=None):
        if y:
            self.ctx.scale(x, y)
        else:
            self.ctx.scale(x, x)
        return self

    def translate(self, x, y):
        self.ctx.translate(x, y)
        return self

    def background(self, color):
        if color:
            self.ctx.save()
            self.ctx.set_matrix(self.initial_matrix)
            self.ctx.rectangle(0, 0, self.pixelSize[0], self.pixelSize[1])
            self.setColor(color)
            self.ctx.fill()
            self.ctx.restore()
        return self

    def fill(self, color):
        self.fillColor = color
        return self

    def noFill(self):
        self.fillColor = None
        return self

    def stroke(self, color):
        self.strokeColor = color
        return self

    def noStroke(self):
        self.strokeColor = None
        return self

    def strokeWeight(self, weight):
        self.lineWidth = weight
        return self

    def line(self, x0, y0, x1, y1):
        self.ctx.move_to(x0, y0)
        self.ctx.line_to(x1, y1)
        self.fillStroke()
        return self

    def rectMode(self, mode):
        self.vRectMode = mode
        return self

    def ellipseMode(self, mode):
        self.vEllipseMode = mode
        return self

    def point(self, a, b):
        if self.strokeColor:
            self.ctx.rectangle(a, b, 1, 1)
            self.setColor(self.strokeColor)
            self.ctx.fill()
        return self

    def rect(self, a, b, c, d):
        cx, cy, rx, ry = convertMode(self.vRectMode, a, b, c, d)
        self.ctx.rectangle(cx-rx, cy-ry, 2*rx, 2*ry)
        self.fillStroke()
        return self

    def triangle(self, x0, y0, x1, y1, x2, y2):
        self.ctx.move_to(x0, y0)
        self.ctx.line_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.close_path()
        self.fillStroke()
        return self

    def quad(self, x0, y0, x1, y1, x2, y2, x3, y3):
        self.ctx.move_to(x0, y0)
        self.ctx.line_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.line_to(x3, y3)
        self.ctx.close_path()
        self.fillStroke()
        return self

    def ellipse(self, a, b, c, d):
        cx, cy, rx, ry = convertMode(self.vEllipseMode, a, b, c, d)
        self.ctx.save()
        self.ctx.translate(cx, cy)
        self.ctx.scale(rx, ry)
        self.ctx.arc(0, 0, 1, 0, 2*math.pi)
        self.ctx.restore()
        self.fillStroke()
        return self

    def arc(self, a, b, c, d, start, end, mode=OPEN):
        cx, cy, rx, ry = convertMode(self.vEllipseMode, a, b, c, d)
        self.ctx.save()
        self.ctx.translate(cx, cy)
        self.ctx.scale(rx, ry)
        if mode == OPEN:
            self.ctx.arc(0, 0, 1, start, end)
        elif mode == CHORD:
            self.ctx.arc(0, 0, 1, start, end)
            self.ctx.close_path()
        elif mode == PIE:
            self.ctx.move_to(0, 0)
            self.ctx.arc(0, 0, 1, start, end)
            self.ctx.close_path()
        self.ctx.restore()
        self.fillStroke()
        return self

    def polygon(self, points, close=True):
        first = True
        for p in points:
            if first:
                self.ctx.move_to(*p)
                first = False
            else:
                self.ctx.line_to(*p)
        if close:
            self.ctx.close_path()
        self.fillStroke()
        return self



def makeImage(outfile, draw, pixelSize, width=None, height=None,
              startX=0, startY=0, background=None, channels=3):
    '''
    Create a PNG file using cairo
    :param outfile: Name of output file
    :param draw: the draw function
    :param pixelSize: size in pixels tuple (x, y)
    :param width: width in user coords
    :param height: height in user coord
    :param startX: x value of left edge of image, user coords
    :param startY: y value of top edge of image, user coords
    :param background: background color
    :param channels: 3 for rgb, 4 for rgba
    :param extras: optional extra params for draw function
    :return: 
    '''
    if not height and not width:
        width = pixelSize[0]
        height = pixelSize[1]
    elif not height:
        height = width * pixelSize[1] / pixelSize[0]
    elif not width:
        width = height * pixelSize[0] / pixelSize[1]

    fmt = cairo.FORMAT_ARGB32 if channels==4 else cairo.FORMAT_RGB24
    surface = cairo.ImageSurface(fmt, pixelSize[0], pixelSize[1])
    ctx = cairo.Context(surface)
    canvas = Canvas(ctx, pixelSize).background(background)
    canvas.scale(pixelSize[0] / width, pixelSize[1] / height).translate(-startX, -startY)
    draw(canvas)
    surface.write_to_png(outfile)

