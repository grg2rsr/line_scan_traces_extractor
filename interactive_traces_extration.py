# -*- coding: utf-8 -*-
"""
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

class interactive_traces_extract(object):
    """ 
    interactively extract traces from line scan images. Image has to be in
    the format of x: time, y: line index, so each horizontal line of pixels 
    represents one scan of the traces, the line below is the next etc.
    
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
                     'origin':'upper',
                     'aspect':0.01} 
                     
        AxesImage = plt.imshow(self.data,**im_params)
        self.im_ax = AxesImage.axes
        self.im_fig = AxesImage.figure
        self.im_ax.set_xlabel('place [px]')
        self.im_ax.set_ylabel('line number')
        
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
        self.traces_fig = plt.figure()
        self.traces_ax = self.traces_fig.add_subplot(111)
        tempTrace_params = {'linewidth':2,
                            'color':'red'}
                            
        self.tempTrace, = self.traces_ax.plot(sp.zeros(self.nLines),**tempTrace_params)
        self.traces_ax.set_xlabel('line number')
        if prestim_frames:
            self.traces_ax.set_ylabel('dF/F')
        else:
            self.traces_ax.set_ylabel('intensity [au]')
    
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
        outpath = os.path.splitext(self.path)[0]+'_traces.csv'
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
            self.traces_ax.plot(self.slice_trace(*self.xs),lw=1,color='grey')
            
            rect = Rectangle((self.xs[0],0),self.width,self.nLines,facecolor='grey',alpha=0.5)
            self.im_ax.add_patch(rect)
        
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
        self.traces_ax.relim()
        self.traces_ax.autoscale_view(True,True,True)
        self.traces_fig.canvas.draw()
        
        # update figure
        self.im_fig.canvas.draw()
        
if __name__ == '__main__':

    ### testing
#    path = '/home/georg/python/line_scan_traces_extractor/test_data/ant2_L1_Sum17.lsm'
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

    interactive_traces_extract(path,prestim_frames=prestim_frames)
    
