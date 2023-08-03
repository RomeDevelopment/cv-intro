import numpy as np
import cv2
import matplotlib.pyplot as plt
import random as rand
import lane_detection as ld
from motor_test import test_motor
import time
from pymavlink import mavutil
import something as sm

video = sm.Video()



##AJ Wrote this
def get_lane_center(lanes):
    ##get_slopes_intercepts returns the slope and intercept in a tuple, lanes[0][0] gets the first line in the first lane
    
    center = (ld.get_slopes_intercepts(lanes[0][0])[1] + ld.get_slopes_intercepts(lanes[0][1])[1]) / 2
    for i in range(1, len(lanes)):
        lane_center = (ld.get_slopes_intercepts(lanes[i][0])[1] + ld.get_slopes_intercepts(lanes[i][1])[1]) / 2
        # we get intercepts for line 1 and line 2 for each lane and get the average
        if np.abs(lane_center - 960) < np.abs(center - 960):
            center = lane_center
            slope = (ld.get_slopes_intercepts(lanes[i][0])[0] + ld.get_slopes_intercepts(lanes[i][1])[0]) / 2
##returns average of the two intercepts of the two lines in a lane as center float
##and the average of their slope too
    return center, slope


##Rome wrote this
def recommend_direction(center,slope):
    #Gets if center is within 10 pixels of 960, it returns forward, otherwise gets back to center
    if center< 950:
        return("left")
    elif center>970:
        return("right")
    elif center <970 and center>950:
        return("forward")



def arm_rov(mav_connection):
    """
    Arm the ROV, wait for confirmation
    """
    mav_connection.arducopter_arm()
    print("Waiting for the vehicle to arm")
    mav_connection.motors_armed_wait()
    print("Armed!")

def disarm_rov(mav_connection):
    """
    Disarm the ROV, wait for confirmation
    """
    mav_connection.arducopter_disarm()
    print("Waiting for the vehicle to disarm")
    mav_connection.motors_disarmed_wait()
    print("Disarmed!")

def run_motors_timed(mav_connection, seconds: int, motor_settings: list) -> None:
    """
    Run the motors for a set time
    :param mav_connection: The mavlink connection
    :param time: The time to run the motors
    :param motor_settings: The motor settings, a list of 6 values -100 to 100
    :return: None
    """
    step = 0
    while step < seconds:
        for i in range(len(motor_settings)):
            test_motor(mav_connection=mav_connection, motor_id=i, power=motor_settings[i])
        # time.sleep(0.2)
        step += 0.2

def forward(t, m):
    run_motors_timed(mav_connection, seconds=t, motor_settings=[m, m, -m, -m, 0, 0])
         
def rightstrafe(t, m):
         run_motors_timed(mav_connection, seconds = t, motor_settings= [m, -m, m, -m])

def leftstrafe(t, m):
        run_motors_timed(mav_connection, seconds=t, motor_settings= [ -m, m, -m, m])

def leftturn(t,m):
         run_motors_timed(mav_connection, seconds=t, motor_settings=[-m, m, m, -m, 0, 0])

def rightturn(t, m):
        run_motors_timed(mav_connection, seconds=t, motor_settings=[m, -m, -m, m, 0, 0])

def movetowardlane(direction, turning):
    
    if direction == "right":
        rightstrafe(3, 30)
    if direction == "left":
        leftstrafe(3, 30)
    if direction == "forward":
        forward(3, 30)
    if turning == "turn left":
        leftturn(3, 30)
    if turning == "turn right":
        rightturn(3, 30)

if __name__ == "__main__":
    ####
    # Initialize ROV
    ####

    mav_connection = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    mav_connection.wait_heartbeat()
    # Arm the ROV and wait for confirmation
    arm_rov(mav_connection)
    waited = 0
    while not video.frame_available():
        waited += 1
        print('\r  Frame not available (x{})'.format(waited), end='')
        # cv2.waitKey(30)
    if video.frame_available():
        frame = video.frame()
        img = frame
        a= ld.detect_lines(img, 36, 80, 3)
        b = ld.detect_lanes(a)
        plt.imshow(ld.draw_lanes(img, b))
        plt.show()
        if b == None or len(b) == 0:
            print("no recomended direction")
        else:
            lane_center = get_lane_center(b)
            direction = recommend_direction(lane_center[0])
            turning = ld.recommend_turn(lane_center[1])
            movetowardlane(direction, turning)
    