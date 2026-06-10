#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from nav_msgs.msg import Odometry

filename = "odometry_trajectory.txt"
f = None
count = 0

def callback(msg):
    global f, count
    try:
        t = msg.header.stamp.to_sec()
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation

        line = "{:.9f} {:.12f} {:.12f} {:.12f} {:.12f} {:.12f} {:.12f} {:.12f}\n".format(
            t, p.x, p.y, p.z, o.x, o.y, o.z, o.w)

        if f and not f.closed:
            f.write(line)
            count += 1

            if count % 100 == 0:
                f.flush()

    except Exception as e:
        rospy.logerr("Save failed: %s", str(e))

def listener():
    global f
    rospy.init_node('odometry_saver_node', anonymous=True)

    
    f = open(filename, 'w', encoding='utf-8')

    rospy.Subscriber("/Odometry", Odometry, callback, queue_size=1000)

    rospy.loginfo("Listening to /Odometry, saving to %s", filename)
    
    try:
        rospy.spin()
    finally:
        
        if f and not f.closed:
            f.flush()
            f.close()
            rospy.loginfo("The file has been safely saved and closed。")

if __name__ == '__main__':
    listener()
