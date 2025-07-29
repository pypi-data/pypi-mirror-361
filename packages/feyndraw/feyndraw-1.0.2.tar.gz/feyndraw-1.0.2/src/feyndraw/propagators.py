import numpy as np
import matplotlib.patches as mpatches
from .geometry import find_angle, find_length, find_point, find_center_line, rotate, rotate_points, numpyfy
from .basicdraw import arrow,arrow_triangle,line, ba_def, ha_def, da_def

z_def_prop = 1

########################
# Scalars and Fermions #
########################

# Straignt line propagator from point p1 to p2
#    arrw: if True, draw an arrow on the propagator at fraction bp from p1 to p2
#    ba, ha, da: see arrow_triangle()
#    double: if True, draw a double line propagator
def line_propagator(ax,p1,p2,color='k',lw=1,ls='-',arrw=False,bp=0.5,ba=ba_def,ha=ha_def,da=da_def,zorder=z_def_prop,double=False):
	if double:
		hp = 0.01*lw
		parametric_propagator(ax,p1,p2,ts_fs=dts_dfs_scalar,h=0,w=0,lw=lw,color=color,zorder=zorder,hp=hp)
		parametric_propagator(ax,p1,p2,ts_fs=dts_dfs_scalar,h=0,w=0,lw=lw,color=color,zorder=zorder,hp=-hp)
	else:
		line(ax,p1,p2,color=color,lw=lw,ls=ls,zorder=zorder)
	if arrw:
		theta = find_angle(p1,p2)
		c = find_point(p1,p2,bp)
		arrow_triangle(ax,c,theta=theta,ba=ba,ha=ha,da=da,color=color,zorder=zorder)

# Line propagator, dashed line without arrow by default
def scalar_propagator(ax,p1,p2,ls='--',arrw=False,**kwargs):
	line_propagator(ax,p1,p2,ls=ls,arrw=arrw,**kwargs)

# Line propagator, full line with arrow by default
def fermion_propagator(ax,p1,p2,ls='-',arrw=True,**kwargs):
	line_propagator(ax,p1,p2,ls=ls,arrw=arrw,**kwargs)

# Line propagator, full line with reversed arrow by default
def antifermion_propagator(ax,p1,p2,ls='-',arrw=True,**kwargs):
	line_propagator(ax,p2,p1,ls=ls,arrw=arrw,**kwargs)

######################
# Photons and Gluons #
######################

# Parametric propagator from point p1 to p2, with a function ts_fs that returns the offsets (ts,fs) at given ts_init
#    h,w: height and frequency parameters for the ts_fs function
#    hp: height parameter for the ts_fs function, used to draw double propagators
def parametric_propagator(ax,p1,p2,ts_fs,h,w,hp=0.1,lw=1,color='k',zorder=z_def_prop):
	ts_init = np.linspace(0,find_length(p1,p2),1000)
	ts, fs = ts_fs(ts_init,h,w,hp)
	p1x,p1y = p1
	xs, ys = rotate(p1,find_angle(p1,p2),p1x+ts_init+ts,p1y+fs)
	ax.plot(xs, ys, color=color, lw=lw, zorder=zorder)

# Function to return offsets (ts,fs) to a line propagator, for different types of propagators
#    h,w: height and frequency parameters for the ts_fs function
#    hp: height parameter for the ts_fs function, used to draw double propagators
def ts_fs_scalar(ts_init,h,w,hp=0):
	return np.zeros(len(ts_init)),np.zeros(len(ts_init))

def ts_fs_photon(ts_init,h,w,hp=0):
	return np.zeros(len(ts_init)),h*np.sin(np.sin(np.sin(ts_init*w*np.pi)))

def ts_fs_gluon(ts_init,h,w,hp=0):
	return h*np.sin(ts_init*w*np.pi),h*np.cos(ts_init*w*np.pi)

# double propagators; g = df/dt
def gs_photon(t,h,w):
	return h * np.pi * w * np.cos(np.pi * t * w) * np.cos(np.sin(np.pi * t * w)) * np.cos(np.sin(np.sin(np.pi * t * w)))

def gs_scalar(ts_init,h,w):
	return 0

def dts_dfs(ts_init,h,w,hp,gs):
	prefactors = hp/np.sqrt(1 + (gs(ts_init,h,w))**2)
	dts = prefactors*gs(ts_init,h,w)
	dfs = -prefactors
	return dts, dfs

def dts_dfs_photon(ts_init,h,w,hp=0.1):
	ts,fs = ts_fs_photon(ts_init,h,w,hp)
	return numpyfy([ts,fs]) + dts_dfs(ts_init,h,w,hp,gs=gs_photon) 

def dts_dfs_scalar(ts_init,h,w,hp=0.1):
	ts,fs = ts_fs_scalar(ts_init,h,w,hp)
	return dts_dfs(ts_init,h,w,hp,gs=gs_scalar)

# Photon (wavy-line) propagator from point p1 to p2
#    h,w: height and frequency parameters for the ts_fs function
#    double: if True, draw a double line propagator
def photon_propagator(ax,p1,p2,h=0.07,w=12,color='k',lw=1,ls='-',zorder=z_def_prop,double=False):
	if double:
		hp = 0.01*lw
		parametric_propagator(ax,p1,p2,ts_fs=dts_dfs_photon,h=h,w=w,lw=lw,color=color,zorder=zorder,hp=hp)
		parametric_propagator(ax,p1,p2,ts_fs=dts_dfs_photon,h=h,w=w,lw=lw,color=color,zorder=zorder,hp=-hp)
	else:
		parametric_propagator(ax,p1,p2,ts_fs=ts_fs_photon,h=h,w=w,lw=lw,color=color,zorder=zorder)

# Gluon (helix) propagator from point p1 to p2
#    h,w: height and frequency parameters for the ts_fs function
def gluon_propagator(ax,p1,p2,h=0.07,w=12,color='k',lw=1,ls='-',zorder=z_def_prop):
	parametric_propagator(ax,p1,p2,ts_fs=ts_fs_gluon,h=h,w=w,lw=lw,color=color,zorder=zorder)

