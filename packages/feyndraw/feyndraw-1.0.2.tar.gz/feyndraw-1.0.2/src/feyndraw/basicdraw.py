import numpy as np
import matplotlib.patches as mpatches
from .geometry import numpyfy,find_angle, find_angles, find_arc_angle, find_length, find_point, find_center, rotate, rotate_points

ba_def = 0.09
ha_def = 0.1
da_def = 0.02

z_def_line = 1
z_def_arrow = 3

# Returns a paler color from the given color
#   color: must be in format (r,g,b)
#   fr: in [0,1], higher means paler
def paler_color(color,fr=0.75):
	dc = fr*(1-np.min(color))
	return (np.clip(dc+color[0],0.0,1.0),np.clip(dc+color[1],0.0,1.0),np.clip(dc+color[2],0.0,1.0))

# Draw a line between two points p1 and p2
def line(ax,p1,p2,color='k',lw=1,ls='-',zorder=z_def_line):
	x1,y1 = p1
	x2,y2 = p2
	ax.plot([x1,x2], [y1,y2],lw=lw,ls=ls,color=color,zorder=zorder)

# Draw the triangle of an arrow
#   c: centroid of the triangle, format [cx,cy]
#   theta: angle (counter-clockwise) of the arrow with respect to the x-axis
#   ba: base of the triangle
#   ha: height of the triangle
#	da: distance between base and dip of the triangle
def arrow_triangle(ax,c,theta=0,ba=ba_def,ha=ha_def,da=da_def,color='k',zorder=z_def_line):
	c = numpyfy(c)
	pts = c + [[2*ha/3,0],[-ha/3,ba/2],[-ha/3+da,0],[-ha/3,-ba/2]]
	pts = rotate_points(c,theta,pts)
	ax.add_patch(mpatches.Polygon(pts,closed=True,fill=True,fc=color,ec=color,joinstyle='round',zorder=zorder))

# Draw the triangle of an arrow on an arc going from p1 to p2
#   p1, p2: points where the arrow is placed
#   bp: fraction of the arc length to rotate the arrow
#   dr: see arc()
#   ba, ha, da: see arrow_triangle()
def arc_arrow_triangle(ax,p1,p2,dr=0,bp=0.5,ba=ba_def,ha=ha_def,da=da_def,color='k',zorder=z_def_line,clockwise=False):
	phase = np.pi/2
	if clockwise: p1,p2, phase = p2,p1,3*np.pi/2
	else: phase = np.pi/2
	c = find_center(p1,p2,dr)
	theta1, theta2 = find_angles(c,p1,p2)
	theta= bp*(theta2-theta1)
	arrow_triangle(ax,rotate_points(c,theta,p1),theta=phase+theta1+theta,ba=ba,ha=ha,da=da,color=color,zorder=zorder)

# Draw an arrow with pointy end from point p1 to p2
#   ba, ha, da: see arrow_triangle()
def arrow(ax,p1,p2,ba=ba_def,ha=ha_def,da=da_def,color='k',lw=1,zorder=z_def_arrow):
	x1,y1 = p1
	x2,y2 = p2
	theta = find_angle(p1,p2)
	line(ax,p1,p2,color=color,lw=lw,zorder=zorder)
	arrow_triangle(ax,p2,theta=theta,ba=ba,ha=ha,da=da,color=color,zorder=zorder)

# Draw an arrow with pointy end over a linear propagator going from p1 to p2
#   b1, b2: fraction of the propagator length to clip at p1 and p2, respectively
#   hp: height between the arrow and the propagator joining p1 and p2; can be negative
#   ba, ha, da: see arrow_triangle()
def arrow_momentum(ax,p1,p2,b1=0.2,b2=0.2,hp=0.1,ba=ba_def,ha=ha_def,da=da_def,color='k',lw=1,zorder=z_def_arrow):
	theta = find_angle(p1,p2)
	L = find_length(p1,p2)-2*ha/3 #correction to have the arrow point be the end of the propagator if b2=0
	pts = [numpyfy(p1) + [b1*L,hp],numpyfy(p1) + [(1-b2)*L,hp]]
	p1a,p2a = rotate_points(p1,theta,pts)
	arrow(ax,p1a,p2a,ba=ba,ha=ha,da=da,lw=lw,color=color,zorder=zorder)

# Draws an arc between two points p1 and p2
#   dr: distance between the "center" of the would-be circle and the straight line joining p1 to p2, can be negative
#   ts: translation along the arc, in the direction of the tangent
#   fs: translation along the arc, in the direction of the normal
def arc(ax,p1,p2,dr=0,ts=0,fs=0,color='k',lw=1,ls='-',zorder=z_def_line,clockwise=False):
	if clockwise: p1,p2 = p2,p1
	c = find_center(p1,p2,dr)
	theta1, theta2 = find_angles(c,p1,p2)
	r = find_length(c,p1)
	thetas = np.linspace(theta1,theta2,1000)

	cx,cy = c
	xs = cx + r*np.cos(thetas)+fs*np.cos(thetas)-ts*np.sin(thetas)
	ys = cy + r*np.sin(thetas)+fs*np.sin(thetas)+ts*np.cos(thetas)

	ax.plot(xs,ys,color=color,lw=lw,ls=ls,zorder=zorder)

# Draw an arrow with pointy end over an arched propagator going from p1 to p2
#   b1, b2: fraction of the arc length to clip at p1 and p2, respectively
#   hp: height between the arrow and the arc joining p1 and p2; can be negative
#   ba, ha, da: see arrow_triangle()
#   dr: see arc()
def arrow_momentum_arc(ax,p1,p2,dr=0,b1=0.3,b2=0.3,hp=0.2,ba=ba_def,ha=ha_def,da=da_def,color='k',lw=1,zorder=z_def_arrow,clockwise=False):
	if clockwise:p1,p2 = p2,p1
	c = find_center(p1,p2,dr)
	r = find_length(c,p1)
	theta1, theta2 = find_angles(c,p1,p2)
	theta = (theta2-theta1)
	theta1b,theta2b = theta1+b1*theta, theta2-b2*theta
	thetas = np.linspace(theta1b,theta2b,1000)
	
	cx,cy = c
	xs = cx + (r+hp)*np.cos(thetas)
	ys = cy + (r+hp)*np.sin(thetas)
	ax.plot(xs,ys,lw=lw,color=color)

	if clockwise:theta_lim, phase = theta1b, 3*np.pi/2
	else: theta_lim, phase = theta2b, np.pi/2
	p2b = (cx + (r+hp)*np.cos(theta_lim),cy + (r+hp)*np.sin(theta_lim))
	arrow_triangle(ax,p2b,theta=theta_lim+phase,ba=ba,ha=ha,da=da,color=color,zorder=zorder)
