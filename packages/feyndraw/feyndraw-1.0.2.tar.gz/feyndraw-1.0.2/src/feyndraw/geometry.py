import numpy as np
import matplotlib.patches as mpatches

# Transform a point [x,y] or (x,y) to a numpy array
def numpyfy(a):
	return np.array(a)

#################
# Line geometry #
#################

# Find the angle (counter-clockwise) betwenn x axis and the line p1 -> p2
def find_angle(p1,p2):
	x1,y1 = p1
	x2,y2 = p2
	if x1 == x2:
		if y2>y1: theta = np.pi/2
		else: theta = -np.pi/2
	else:
		theta = np.arctan((y2-y1)/(x2-x1))
		if x2<x1: theta = theta + np.pi
	return theta

# Find length between points p1 and p2
def find_length(p1,p2):
	x1,y1 = p1
	x2,y2 = p2
	return np.sqrt((x1-x2)**2 + (y1-y2)**2)

# Find the point at fraction bp from p1 to p2
def find_point(p1,p2,bp=0.5):
	return (1-bp)*numpyfy(p1) + bp*numpyfy(p2)

def find_center_line(p1,p2):
	return find_point(p1,p2,bp=0.5)

###################
# Circle geometry #
###################

# Find the two angle (counter-clockwise) 
#   theta1: between (c and p1)
#   theta2: between (c and p2) such that theta1 < theta2
def find_angles(c,p1,p2):
	theta1 = find_angle(c,p1)
	theta2 = find_angle(c,p2)
	if theta1 >= theta2: theta2 = theta2 + 2*np.pi
	return theta1, theta2

# Find the angle between two points p1 and p2 with respect to center c
def find_arc_angle(c,p1,p2):
	theta1, theta2 = find_angles(c,p1,p2)
	return theta2 - theta1

# Find the center of the circle that would go through p1 and p2 at distance h from the line joining them
def find_center(p1,p2,dr):
	c_line = find_center_line(p1,p2)
	theta = find_angle(p1,p2)
	return c_line + dr*np.array([np.sin(theta), -np.cos(theta)])

#############
# Rotations #
#############

# rotate points [t,f] by theta around c by angle theta
#   ts = [t1,t2,...] and f = [f1,f2,...] for points [t1,f1], [t2,f2]...
def rotate(c,theta,ts,fs):
	cx,cy = c
	xs = cx + (ts-cx)*np.cos(theta) - (fs-cy)*np.sin(theta)
	ys = cy + (ts-cx)*np.sin(theta) + (fs-cy)*np.cos(theta)
	return xs,ys

# rotate points pts by theta around c by angle theta
#   pts = [[x1,y1],[x2,y2],...]
def rotate_points(c,theta,pts):
	pts = np.transpose(numpyfy(pts))
	pts = rotate(c,theta,pts[0],pts[1])
	return np.transpose(pts)