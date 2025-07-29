import numpy as np
import matplotlib.patches as mpatches
from matplotlib.colors import to_rgb
from .basicdraw import line, paler_color
from .geometry import numpyfy, rotate_points

z_def_vertex = 2

# Blob at center c and radius r
#   fr_fc: see paler_color()
def blob(ax,c,r=0.2,hatch='\\\\\\\\',color='k',lw=1,fr_fc=0.75,zorder=z_def_vertex):
	ec = to_rgb(color)
	fc = paler_color(ec,fr=fr_fc)
	ax.add_patch(mpatches.Circle(c,r,fill=True,hatch=hatch,fc=fc,ec=ec,lw=lw,zorder=zorder))

# Draw an X for oscillations at center c, rotated by theta, with leg length b, linewidth lw
def oscillation_x(ax,c,theta=0,b=0.1,color='k',lw=5,zorder=z_def_vertex):
	pts = numpyfy(c) + [[-b,-b],[b,b],[-b,b],[b,-b]]
	p1,p2,p3,p4 = rotate_points(c,theta,pts)
	line(ax,p1,p2,color=color,lw=lw,zorder=zorder)
	line(ax,p3,p4,color=color,lw=lw,zorder=zorder)
