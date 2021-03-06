#!/usr/bin/env python
import os
import rospy
import rospkg
import numpy as np
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from python_qt_binding.QtCore import QTimer, Slot

from mcptam_msgs.msg import SystemInfo
from mcptam_msgs.msg import TrackerState
from mcptam_msgs.srv import Reset
from std_srvs.srv import Empty

class SysmonWidget(QWidget):
  _last_info_msg = SystemInfo()
  _last_tracker_msg = TrackerState()
  _slam_info_sub = None
  _slam_tracker_sub = None
  _slam_init_srv = None
  _slam_reset_srv = None
  _mcptam_namespace = None
  _num_received_msgs = 0
  def __init__(self, mcptam_namespace='mcptam'):
    
    # Init QWidget
    super(SysmonWidget, self).__init__()
    self.setObjectName('SysmonWidget')
    
    # load UI
    ui_file = os.path.join(rospkg.RosPack().get_path('artemis_sysmon'), 'resource', 'widget.ui')
    loadUi(ui_file, self)
            
    # Subscribe to ROS topics and register callbacks
    self._slam_info_sub = rospy.Subscriber(mcptam_namespace+'/system_info', SystemInfo, self.slam_info_cb)
    self._slam_tracker_sub = rospy.Subscriber(mcptam_namespace+'/tracker_state', TrackerState, self.slam_tracker_cb)
    
    # Initialize service call
    print('Waiting for MAV services')
    rospy.wait_for_service(mcptam_namespace+'/init')
    rospy.wait_for_service(mcptam_namespace+'/reset')
    print('Connected to SLAM system')
    self._slam_init_srv = rospy.ServiceProxy(mcptam_namespace+'/init', Empty)
    self._slam_reset_srv = rospy.ServiceProxy(mcptam_namespace+'/reset', Reset)
   
    # init and start update timer for data, the timer calls the function update_info all 40ms    
    self._update_info_timer = QTimer(self)
    self._update_info_timer.timeout.connect(self.update_info)
    self._update_info_timer.start(40)
    
    # set the functions that are called when a button is pressed
    self.button_start.pressed.connect(self.on_start_button_pressed)
    self.button_reset.pressed.connect(self.on_reset_button_pressed)
    self.button_quit.pressed.connect(self.on_quit_button_pressed)

  @Slot(str)       
  def slam_info_cb(self, msg):
    self._last_info_msg = msg
    self._num_received_msgs += 1
    
  def slam_tracker_cb(self, msg):
    self._last_tracker_msg = msg
    self._num_received_msgs += 1

  def update_info(self):
    info_text = 'Waiting for MAV connection'
    if self._num_received_msgs > 0:
      # Tracker FPS
      info_text = 'fps = %.2f' % self._last_info_msg.dFPS
      info_text += '\n'
      # System State
      info_text += self._last_info_msg.message
      info_text += '\n'

    # set info text
    self.mcptam_info_label.setText(info_text)
        
  def on_start_button_pressed(self):
    print('Requesting SLAM init')
    self.slam_init()
    
  def on_reset_button_pressed(self):
    print('Requesting SLAM reset')
    self.slam_reset()
    
  def on_quit_button_pressed(self):
    print('Quitting SLAM')
    self.slam_quit()
    
  def slam_init(self):
    try:
        r = _slam_init_srv() # handle response TODO
    except rospy.ServiceException as exc:
        print("Init request failure" + str(exc))

  def slam_reset(self):
    try:
        r = _slam_reset_srv(true, false) # handle response TODO
    except rospy.ServiceException as exc:
        print("Reset request failure" + str(exc))

  def slam_quit(self):
    print("Unimplemented")
    
    
