# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 10:35:03 2015

@author: georg
"""

"""
#==============================================================================
# USAGE
#==============================================================================

execute this file with python, pass it 1 or 3 arguments

1: path to the file that you want to analyze
2,3 (optional): 2 integer values, if specified, the dF/F will be calculated based
on the signal between those frames. So if your stimulus starts at frame 40, and 
there is too much bleaching at the first 5 frames, you would run


python interactive_trajectory_extractor.py path_to_lsm_file 5 40


this will open two windows, select a region of interest by moving the mouse over 
it. Scrolling the mouse wheel will change it's y-extent. Middle mouse button 
press will select this region for extraction, an average is made inside the ROI.
Upon closing all windows, a .csv will be written with the x1:x2 coordinates of 
the ROI as the first two lines after the header (which just contains the order
of clicks from 0 on)

happy slicing!

written by Georg Raiser 20.10.2015
questions/bugs to grg2rsr@gmail.com

"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import scipy as sp
import sys
import os
import tifffile
import pandas as pd

class interactive_trajectory_extract(object):
    """ 
    interactively extract trajectories from line scan images. Image has to be in
    the format of x: time, y: line index, so each horizontal line of pixels 
    represents one scan of the trajectory, the line below is the next etc.
    
    """
    def __init__(self,image_path,prestim_frames=None):
        self.path = image_path
        
        ## ini data
        self.data = self.read_image(self.path)
        self.nLines = self.data.shape[0]
        self.nPlaces = self.data.shape[1]
        
        if prestim_frames:
            Fstart,Fstop = prestim_frames
            bck = sp.average(self.data[Fstart:Fstop,:],axis=0)[sp.newaxis,:]
            self.data = (self.data - bck) / bck
        
        ## ini UI
        # Image
        im_params = {'interpolation':'none',
                     'cmap':'jet',
                     'extent':[0,self.nPlaces,self.nLines,0],
                     'origin':'upper'} # image coordinates
                     
        AxesImage = plt.imshow(self.data,**im_params)
        self.im_ax = AxesImage.axes
        self.im_fig = AxesImage.figure
        
        # coordinate calc
        self.pos = int(self.nPlaces/2) # is the position of the mouse pointer
        self.width = 11 # is x1 - x0
        self.xs = self.calc_x(self.pos,self.width) # is a tuple (x0,x1) along which is sliced
        
        
        # add patch
        rect_params = {'facecolor':'red',
                       'alpha':0.5}
                       
        self.Rect = Rectangle(self.xs,self.width,self.nLines,**rect_params)
        self.im_ax.add_patch(self.Rect)
        
        # extracted traces preview
        self.traj_fig = plt.figure()
        self.traj_ax = self.traj_fig.add_subplot(111)
        tempTrace_params = {'linewidth':2,
                            'color':'red'}
                            
        self.tempTrace, = self.traj_ax.plot(sp.zeros(self.nLines),**tempTrace_params)
    
        ## extracting info
        self.coords = []
        self.traces = []    
        
        # hooking up the interactive handles    
        self.im_fig.canvas.mpl_connect('button_press_event', self.mouse_clicked_event)
        self.im_fig.canvas.mpl_connect('scroll_event',self.scroll_event)
        self.im_fig.canvas.mpl_connect('motion_notify_event',self.mouse_moved_event)
        self.im_fig.canvas.mpl_connect('close_event', self.close_event)
        plt.show()
        pass
    
    ### input output
    def read_image(self,path):
        """ dummy reader, to be extended for other file formats """
        return tifffile.imread(path)

    def write_output(self):
        """ write ouput upon closing the image figure """
        outpath = os.path.splitext(self.path)[0]+'_trajectories.csv'
        if len(self.coords) > 0:
            print 'writing to ' + outpath
            coors = pd.DataFrame(sp.array(self.coords).T,index=['x0','x1'])
            values = pd.DataFrame(sp.vstack(self.traces).T)
            Df = pd.concat([coors,values])
            Df.to_csv(outpath)
        else:
            print "exiting without saving anything"

    def close_event(self,event):
        self.write_output()
        plt.close('all')

    def calc_x(self,pos,width):
        """ calculate x0, x1 (slice extent) based on current pos and width """
        if width == 1:
            x0 = pos
            x1 = pos + 1
        else:
            x0 = pos - (width-1)/2
            x1 = pos + (width-1)/2            
        return (x0,x1)
        
    def scroll_event(self,event):
        """ changes width of slice """
        if event.button == 'up':
            self.width += 2
        if event.button == 'down':
            self.width -= 2
            
        self.width = sp.clip(self.width,1,self.nPlaces)
        self.xs = self.calc_x(self.pos,self.width)
        self.Rect.set_xy((self.xs[0] ,0))
        self.Rect.set_width(self.width)
        self.update()
        
    def mouse_moved_event(self,event):
        """ x position of mouse determines center of slice """
        if event.inaxes == self.im_ax:
            self.pos = int(event.xdata)
            self.update()
    
    def mouse_clicked_event(self,event):
        """ middle button click slices """
        if event.button==2:
            self.coords.append(self.xs)
            self.traces.append(self.slice_trace(*self.xs))
            self.traj_ax.plot(self.slice_trace(*self.xs),lw=1,color='grey')
        
    def slice_trace(self,x0,x1):
        sliced = sp.average(self.data[:,x0:x1],axis=1)  
        return sliced
        
    def update(self):
        """ UI update """
        # calc new pos        
        self.xs = self.calc_x(self.pos,self.width)
        
        # update rect
        self.Rect.set_xy((self.xs[0] ,0))
        
        # get new slice
        self.tempTrace.set_ydata(self.slice_trace(*self.xs))
        
        # update traces preview
        self.traj_ax.relim()
        self.traj_ax.autoscale_view(True,True,True)
        self.traj_fig.canvas.draw()
        
        # update figure
        self.im_fig.canvas.draw()
        
if __name__ == '__main__':

    ### testing
#    path = '/home/georg/python/trajectories/steffis_data/ant2_L1_Sum17.lsm'
#    prestim_frames = (0,40)
    
    ### nontesting
    if len(sys.argv) == 1:
        print "no path to data given"
        
    if len(sys.argv) == 2:
        path = sys.argv[1]
        prestim_frames = None
    
    if len(sys.argv) == 4:
        path = sys.argv[1]
        prestim_frames = (int(sys.argv[2]),int(sys.argv[3]))

    interactive_trajectory_extract(path,prestim_frames=prestim_frames)
    
    
    
        

    
    
    
    