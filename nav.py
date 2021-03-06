#!/usr/bin/env python

import rospy
import actionlib
from actionlib_msgs.msg import *
from move_base_msgs.msg import MoveBaseGoal, MoveBaseAction
from geometry_msgs.msg import Twist
from p2os_msgs.msg import MotorState
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import PoseArray
from apriltags_ros.msg import AprilTagDetectionArray
from nav_msgs.msg import Odometry
from frontier_exploration.msg import ExploreTaskAction, ExploreTaskGoal

rate = None
goal_client = None
exploration_client = None
goal_status = 0
found_ids = {}
pose = None

def orientationToAngle(orient):
    angel = 2*math.degrees(math.asin(orient))
    if angel < 0:
        angel += 360
    return angel

def angleToOrientation(angle):
    #angle = angle % 360
    mult = 1
    if angle > 180: mult = -1
    orient = math.sin(math.radians(angle/2))
    if mult < 0:
        orient = mult*orient
    return orient

def moveBaseActionResultHandler(data):
    global goal_status
    goal_status = data.status.goal_id
    #print "status: ", status
    #print data.result
    #http://docs.ros.org/fuerte/api/actionlib_msgs/html/msg/GoalStatus.html

def tagDetectionsHandler(data):
    global found_ids, pose, goal_status, rate

    detections = data.detections

    for detection in detections:
        id = detection.id
        if id not in found_ids:
            size = detection.size
            pose = detection.pose

            #TODO:: how to interrupt exploration_client??

            #TODO:: set up the goal pose!!!
            x = 0 #???
            y = 0 #???
            z_theta = 0 #???

            goal = MoveBaseGoal()
            goal.target_pose.header.frame_id = "map"
            goal.target_pose.header.stamp = rospy.get_rostime()

            goal.target_pose.pose.position.x = x
            goal.target_pose.pose.position.y = y
            goal.target_pose.pose.orientation.z = z_theta

            goal_client.send_goal(goal)

            #wait for the goal to finish!!!
            while goal_status < 3:
                rate.sleep()

            #TODO:: how do restart exploration_client?

def odometryHandler(data):
    global pose
    pose = pose_msg.pose.pose


def main():
    global goal_client, exploration_client, rate
    rospy.init_node('homework4_navigator')
    rate = rospy.Rate(10)
    rospy.Subscriber("/odom", Odometry, odometryHandler)
    rospy.Subscriber("/move_base/result", MoveBaseActionResult, moveBaseActionResultHandler)
    rospy.Subscriber("/tag_detections", AprilTagDetectionArray, tagDetectionsHandler)


    velPub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

    print "."
    print "make sure you start the motors!"

    goal_client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
    exploration_client = actionlib.SimpleActionClient("explore_server", ExploreTaskAction)

    #Waits until the action server has started up and started listening for goals
    goal_client.wait_for_server()
    exploration_client.wait_for_server()

    #TODO
    time = 0
    three_minutes = 3
    # MAIN LOOP
    while time < three_minutes:
        exploration_goal = ExploreTaskGoal
        exploration_goal.explore_boundary.header.seq = 1
        exploration_goal.explore_boundary.header.frame_id = 1
        exploration_goal.explore_center.point.x = 1
        exploration_goal.explore_center.point.y = 0
        exploration_goal.explore_center.point.z = 0

        exploration_client.send_goal(goal)

        #TODO:: how to interrupt exploration_client??


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
