#!/usr/bin/env python
####
# skeleton = heavily based on sample_hw7 sample
# meat and potatoes = not
####
import roslib; roslib.load_manifest('particle_visualizer')
import rospy
import mcl_viz
import mcl_debug
import math
import numpy

from particle_visualizer.msg import particle
from particle_visualizer.msg import particles

def got_particles(msg):
    mcl_viz.parset = [(m.x,m.y,m.t,m.w) for m in msg.particles]

if __name__ == '__main__':
    rospy.init_node("particle_visualizer")
    global receiver
    mcl_viz.mcl_init('particle_visualizer')    
    rospy.Subscriber('/particle', particles, got_particles)
    mcl_viz.mcl_run_viz()
