#!/usr/bin/env python

import math
import numpy

import rospy
import roslib

roslib.load_manifest('jsk_joy')

from sensor_msgs.msg import Joy
import tf.transformations
from joy_status import XBoxStatus, PS3Status
from plugin_manager import PluginManager

class JoyManager():
  def __init__(self):
    self.pre_status = None
    self.controller_type = rospy.get_param('~controller_type', 'xbox')
    self.plugins = rospy.get_param('~plugins', [])
    self.current_plugin_index = 0
    if self.controller_type == 'xbox':
      self.JoyStatus = XBoxStatus
    elif self.controller_type == 'ps3':
      self.JoyStatus = PS3Status
    self.plugin_manager = PluginManager('jsk_joy')
    self.loadPlugins()
  def loadPlugins(self):
    self.plugin_manager.loadPlugins()
    self.plugin_instances = self.plugin_manager.loadPluginInstances(self.plugins)
  def nextPlugin(self):
    rospy.loginfo('switching to next plugin')
    self.current_plugin_index = self.current_plugin_index + 1
    if len(self.plugin_instances) == self.current_plugin_index:
      self.current_plugin_index = 0
    self.current_plugin.disable()
    self.current_plugin = self.plugin_instances[self.current_plugin_index]
    self.current_plugin.enable()
  def start(self):
    if len(self.plugin_instances) == 0:
      rospy.logfatal('no valid plugins are loaded')
      return
    self.current_plugin = self.plugin_instances[0]
    self.current_plugin.enable()
    self.joy_subscriber = rospy.Subscriber('/joy', Joy, self.joyCB)
    
  def joyCB(self, msg):
    status = self.JoyStatus(msg)
    if self.pre_status and status.select and not self.pre_status.select:
      self.nextPlugin()
    else:
      self.current_plugin.joyCB(status)
    self.pre_status = status
    
    
def main():
  global g_manager
  rospy.sleep(1)
  rospy.init_node('jsk_joy')
  g_manager = JoyManager()
  g_manager.start()
  rospy.spin()
  
if __name__ == '__main__':
  main()
  