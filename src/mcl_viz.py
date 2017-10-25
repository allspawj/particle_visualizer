
# mcl_tools
#
# Some utility and visualization functions to help with
# planar Monte Carlo Localization.

import sys
import math
import time
import random
import roslib

MAP_WIDTH  = 53.9
MAP_HEIGHT = 10.6
MAP_PPM    = 10.0 
LASER_MAX  = 5.0

parset    = []
parset2   = []
map_img   = None

real_pose = (0,0,0,0)
best_pose = (0,0,0,0)

try:
    from PIL import Image
    import numpy
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    print "Error importing libraries, try"
    print
    print "OMG    apt-get install python-opengl python-numpy"
    print
    sys.exit(1)
    #from OpenGL.GLUT import *
    #from OpenGL.GL import *
    #from OpenGL.GLU import *

# Generate and sample particles.

import mcl_debug


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


def show_real_pose(particle):
    global real_pose
    real_pose = particle
#    time.sleep(0.01)

def show_best_pose(particle):
    global best_pose
    best_pose = particle
#    time.sleep(0.01)

def gl_display():
    global parset
    global parset2
    global real_pose
    global best_pose

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw background.
    glEnable( GL_TEXTURE_2D )
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)
    glVertex2f(0, 1)
    glTexCoord2f(0, 0)
    glVertex2f(0, 0)
    glTexCoord2f(1, 0)
    glVertex2f(1, 0)
    glTexCoord2f(1, 1)
    glVertex2f(1, 1)
    glEnd()

    # Draw particles.
    glDisable( GL_TEXTURE_2D )
    glColor3f(0.0, 1.0, 0.0)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for pt in parset:
        (x, y, theta, w) = pt
        x = x / MAP_WIDTH
        y = y / MAP_HEIGHT
        glVertex2f(x, y)
    glEnd()

    # Draw poses
    glPointSize(5.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(real_pose[0] / MAP_WIDTH, real_pose[1] / MAP_HEIGHT)
    glColor3f(0.0, 0.3, 1.0)    
    glVertex2f(best_pose[0] / MAP_WIDTH, best_pose[1] / MAP_HEIGHT)
    glEnd()

    glutSwapBuffers()


def gl_idle():
    glutPostRedisplay()

def gl_click(button, state, px, py):
    if button != 0 or state != 1:
        return

    wx = px_to_wx(px)
    wy = py_to_wy(py)

    print "Click at world =", wx, wy, "; image =", px, py, "; hit =", map_hit(wx, wy)

def mcl_init(pkg_name):
    global map_img
    global raycaster

    pkg_dir = roslib.packages.get_pkg_dir(pkg_name)
    map_img = Image.open(pkg_dir + "/hallway.png")
    (ww, hh) = map_img.size

    print "pixels per meter:", ww / MAP_WIDTH

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(ww, hh)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(sys.argv[0])

    gluOrtho2D(0.0, 1.0, 0.0, 1.0)

    glEnable( GL_POINT_SMOOTH );
    glEnable( GL_BLEND );
    glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
    glPointSize( 1.0 );

    glClearColor ( 0, 0, 0, 0 )
    glShadeModel( GL_SMOOTH )
    glDisable( GL_LIGHTING )
    glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
    glTexImage2D( GL_TEXTURE_2D, 0, 3, ww, hh, 0, GL_RGB, GL_UNSIGNED_BYTE, 
                  map_img.tostring("raw", "RGB", 0, -1))
    glEnable( GL_TEXTURE_2D )

    glutDisplayFunc(gl_display)
    glutIdleFunc(gl_idle)    
    glutMouseFunc(gl_click)

def mcl_run_viz():
    glutMainLoop()
