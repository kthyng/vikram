'''
Script to run drifters at 1km initial spacing daily forward for 30 days.
'''

import matplotlib as mpl
mpl.use("Agg") # set matplotlib to use the backend that does not require a windowing system
import numpy as np
import os
import netCDF4 as netCDF
import pdb
import matplotlib.pyplot as plt
import tracpy
from datetime import datetime, timedelta
import glob
from tracpy.tracpy_class import Tracpy
import tracpy.plotting

def init():

    currents_filename = 'bp9_his_000?.nc'
    grid_filename = 'bp9_his_0001.nc'

    time_units = 'seconds since 0001-01-01'

    nsteps = 5 

    # Number of steps to divide model output for outputting drifter location
    N = 5

    # Number of days
    ndays = 1.5

    # This is a forward-moving simulation
    ff = 1 

    # Time between outputs
    tseas = 24*3600 # 4 hours between outputs, in seconds, time between model outputs 
    ah = 0. # old tracks: 5.
    av = 0. # m^2/s

    # Initial lon/lat locations for drifters
    # There need to be at least 2 drifters
    lat0 = np.array([24, 24])
    lon0 = np.array([-93, -93.05])

    # surface drifters
    z0 = 's'  
    zpar = 49 

    # for 3d flag, do3d=0 makes the run 2d and do3d=1 makes the run 3d
    do3d = 0
    doturb = 0

    # Flag for streamlines. All the extra steps right after this are for streamlines.
    dostream = 0

    # Initialize Tracpy class
    tp = Tracpy(currents_filename=currents_filename, grid_filename=grid_filename, tseas=tseas, ndays=ndays, nsteps=nsteps, dostream=dostream, savell=True, doperiodic=0, 
                N=N, ff=ff, ah=ah, av=av, doturb=doturb, do3d=do3d, z0=z0, zpar=zpar, time_units=time_units, usebasemap=True)

    return tp, lon0, lat0


def run():

    # Make sure necessary directories exist
    if not os.path.exists('tracks'):
        os.makedirs('tracks')
    if not os.path.exists('figures'):
        os.makedirs('figures')
        
    # For when to start simulations running.
    # Let's only start one (they start every 24 hours)
    overallstartdate = datetime(0001, 1, 1, 0, 0)
    overallstopdate = datetime(0001, 1, 2, 0, 0)

    date = overallstartdate

    # Start from the beginning and add days on for loop
    # keep running until we hit the next month
    while date < overallstopdate:

        name = date.isoformat()[0:13]

        # If the particle trajectories have not been run, run them
        if not os.path.exists('tracks/' + name + '.nc') and \
            not os.path.exists('tracks/' + name + 'gc.nc'):

            # Read in simulation initialization
            tp, lon0, lat0 = init()

            # Run tracpy
            lonp, latp, zp, t, T0, U, V = tracpy.run.run(tp, date, lon0, lat0)

        # Increment by 24 hours for next loop, to move through more quickly
        # nh = nh + 24
        date = date + timedelta(hours=24)

    # Plot
    tracpy.plotting.background(grid=tp.grid)
    xp, yp = tp.grid['basemap'](lonp, latp)
    plt.plot(xp.T, yp.T, 'k')
    plt.plot(xp[:,0], yp[:,0], 'go') # starting locations
    plt.plot(xp[:,-1], yp[:,-1], 'ro') # stopping locations
    plt.show()


if __name__ == "__main__":
    run()    
