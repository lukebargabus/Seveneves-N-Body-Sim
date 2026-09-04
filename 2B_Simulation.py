'''
Create 3D Coordinate System

Create Objects (to start, Earth and Moon), initial positions and velocities, masses

G = ...

Create time system starting at 0


Compute initial acceleration (a)

for each time step:
    for each object:
        for x,y,z: (leapfrog integration)
            v_half = v + a * (dt/2)
            x_new = x + v_half * dt
            a_new = compute acceleration from forces with x_new
            v_new = v_half + a_new * (dt/2)
            
            save x_new, v_new to document
            
            #preapre for next step
            x = x_new
            v = v_new
            a = a_new

'''

import numpy as np
import pandas as pd

#setting up constants / definitions
G_SI = 6.674e-11
M_earth_kg = 5.972e24
D_earth_moon_m = 3.844e8
day_s = 86400

G = G_SI * M_earth_kg * day_s**2 / D_earth_moon_m**3

t = 0
t_end = 100
dt = 1

M_earth = 1
M_moon = 0.0123


#inital velocity calculation

v_rel = np.sqrt(G * (M_earth + M_moon))

v_moon  =  v_rel * (M_earth / (M_earth + M_moon)) * np.array([0, 1, 0])
v_earth = -v_rel * (M_moon  / (M_earth + M_moon)) * np.array([0, 1, 0])

#define object arrays

# [m,x,y,z,vx,vy,vz,ax,ay,az]
E = np.array([M_earth,0,0,0,v_earth[0],v_earth[1],v_earth[2],0,0,0])
M0 = np.array([M_moon,1,0,0,v_moon[0],v_moon[1],v_moon[2],0,0,0])




#calculate initial force -> acceleration

F0 = np.array([0,0,0]) #x,y,z
F = G * E[0] * M0[0] / np.sqrt((E[1]-M0[1])**2 + (E[2]-M0[2])**2 + (E[3]-M0[3])**2)
F0[0] = F * np.sqrt((E[1]-M0[1])**2) #x
F0[1] = F * np.sqrt((E[2]-M0[2])**2) #y
F0[2] = F * np.sqrt((E[3]-M0[3])**2) #z

E[7] = F0[0] / E[0]
E[8] = F0[1] / E[0]
E[9] = F0[2] / E[0]

M0[7] = F0[0] / M0[0]
M0[8] = F0[1] / M0[0]
M0[9] = F0[2] / M0[0]

#THE LOOP

Objects = [E, M0]

history = []  


for i in range(t, t_end):
    # Phase 1: half-kick velocities for ALL objects, using OLD accel
    for j in Objects:
        j[4:7] = j[4:7] + j[7:10] * (dt/2)

    # Phase 2: drift positions for ALL objects, using half-kicked velocity
    for j in Objects:
        j[1:4] = j[1:4] + j[4:7] * dt

    # Phase 3: recompute acceleration for ALL objects using NEW positions
    #          (only now do E and M0 both have their final, updated positions)
    for j, other in [(E, M0), (M0, E)]:
        r_vec = other[1:4] - j[1:4]
        r = np.linalg.norm(r_vec)
        j[7:10] = G * other[0] * r_vec / r**3

    # Phase 4: second half-kick, using NEW accel
    for j in Objects:
        j[4:7] = j[4:7] + j[7:10] * (dt/2)

    # save state
    for j in Objects:
        history.append({"t": i, "obj": j[0], "x": j[1], "y": j[2], "z": j[3],
                         "vx": j[4], "vy": j[5], "vz": j[6]})

    i += dt
df = pd.DataFrame(history)
df.to_parquet("sim_output.parquet", index=False)
