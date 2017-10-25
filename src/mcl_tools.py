
# mcl_tools
#
# Some utility and visualization functions to help with
# planar Monte Carlo Localization.

import sys
import math
import time
import random
import roslib

# You'll need to go into src/raycaster and type "make"
# to build the C extension.
try:
    from raycaster import *
except:
    print "Error importing raycaster extension, do"
    print
    print "    sudo apt-get install swig"
    print "    (roscd sample_hw7/src/raycaster && make)"
    print
    sys.exit(1)

MAP_WIDTH  = 53.9
MAP_HEIGHT = 10.6
MAP_PPM    = 10.0 
LASER_MAX  = 5.0

parset    = []
map_img   = None
raycaster = None

real_pose = (0,0,0,0)
best_pose = (0,0,0,0)

from PIL import Image
import numpy

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
    print "Error importing libraries, try"
    print
    print "OMG    apt-get install python-opengl python-numpy"
    print
#    sys.exit(1)

# Generate and sample particles.

import mcl_debug

def random_particle():
    x = random.uniform(0, MAP_WIDTH)
    y = random.uniform(0, MAP_HEIGHT)
    t = random.uniform(0, 2*math.pi)
    w = random.uniform(0, 1)
    return (x, y, t, w)

def random_sample(xs, size, p):
    p = numpy.array(p, dtype=numpy.double, ndmin=1, copy=0)
    cdf = p.cumsum()
    cdf /= cdf[-1]
    uniform_samples = numpy.random.random(size)
    idx = cdf.searchsorted(uniform_samples, side='right')
    return map(lambda ii: xs[ii], idx)

# Operations to convert world <-> image pixel coords.

def clamp(xx, x0, x1):
    return int(min(max(xx, x0), x1))

def wx_to_px(wx):
    global map_img
    (ww, hh) = map_img.size
    return clamp((wx / MAP_WIDTH) * ww, 0, ww - 1)

def wy_to_py(wy):
    global map_img
    (ww, hh) = map_img.size
    return hh - clamp((wy / MAP_HEIGHT) * hh, 0, hh - 1)

def px_to_wx(px):
    global map_img
    (ww, hh) = map_img.size
    return (float(px)/ww) * MAP_WIDTH

def py_to_wy(py):
    global map_img
    (ww, hh) = map_img.size
    return MAP_HEIGHT - ((float(py)/hh) * MAP_HEIGHT)

def wt_to_pt(pt):
    x = math.cos(pt)
    y = math.sin(pt)
    return math.atan2(-y, x)

# Operations to perform raycasting on the map image.

def map_hit(wx, wy):
    global raycaster
    global map_img
    (ww, hh) = map_img.size

    px = wx_to_px(wx)
    py = wy_to_py(wy)

    wall = raycaster_test_pixel(raycaster, px, py)
    return wall == 1

def map_range(particle, phi):
    global raycaster
    global map_img
    (ww, hh) = map_img.size

    (wx, wy, theta, weight) = particle
    px = wx_to_px(wx)
    py = wy_to_py(wy)
    pt = wt_to_pt(theta+phi)

    return raycaster_cast(raycaster, px, py, pt)


def mcl_init(pkg_name):
    global map_img
    global raycaster

    pkg_dir = roslib.packages.get_pkg_dir(pkg_name)
    map_img = Image.open(pkg_dir + "/hallway.png")
    (ww, hh) = map_img.size

    print "pixels per meter:", ww / MAP_WIDTH

    raycaster = raycaster_init(pkg_dir + "/hallway.png")
