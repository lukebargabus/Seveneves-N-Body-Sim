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
dt = .1

M_earth = 1
M_moon = 0.0123

# Object Format: [m,x,y,z,vx,vy,vz,ax,ay,az]
def Make_Object(Mass, Pos, Vel):
    Obj = np.zeros(10)
    Obj[0] = Mass
    Obj[1:4] = Pos
    Obj[4:7] = Vel
    return Obj

def Calc_Acc(Obj):
    for obj in Obj: #reset to 0 so that acceleration doesn't accumulate
        obj[7:10] = 0
    for i, obj_i in enumerate(Obj):
        for j, obj_j in enumerate(Obj):
            if i == j:
                continue
            r_vec = obj_j[1:4] - obj_i[1:4]
            r = np.linalg.norm(r_vec)
            obj_i[7:10] += G * obj_j[0] * r_vec / r**3


#Treats Earth as a stationary center (ok approx for our specific simulation)
#Normal is z-axis, cross product is taken with it, so test objects cannot lie on the z axis without changing normal
def Circular_Orbit_Velocity(pos, M_central, normal=[0,0,1]):
    pos = np.array(pos, dtype=float)
    normal = np.array(normal, dtype=float)
    normal = normal / np.linalg.norm(normal)   # ensure it's a unit vector
    r = np.linalg.norm(pos)
    speed = np.sqrt(G * M_central / r)
    tangent = np.cross(normal, pos)
    tangent = tangent / np.linalg.norm(tangent)
    return speed * tangent

#temporary initials for non-Earth objects
moon_pos = [0,1,0]
v_moon = Circular_Orbit_Velocity(moon_pos, M_earth)

pos_3 = [0,1,0.3]
v_3 = Circular_Orbit_Velocity(pos_3, M_earth)



# just 2 for now
Objects = [
    Make_Object(M_earth, [0,0,0], [0,0,0]), #Earth, velocity adjusted right after
    Make_Object(M_moon, moon_pos, v_moon), #Moon
    Make_Object(M_moon, pos_3, v_3) #Moon 2 for testing
    ]


# fix Earth's velocity so total momentum = 0
total_p = sum(obj[0] * obj[4:7] for obj in Objects[1:])  # momentum of everyone except Earth
Objects[0][4:7] = -total_p / Objects[0][0] # v = total p (mv) / M, remainder is Earth


#calculate initial acceleration
Calc_Acc(Objects)



#THE LOOP

history = []  


for i in range(t, t_end):
    # step 1: half-kick velocities for ALL objects, using OLD accel
    for j in Objects:
        j[4:7] = j[4:7] + j[7:10] * (dt/2)

    # step 2: drift positions for ALL objects, using half-kicked velocity
    for j in Objects:
        j[1:4] = j[1:4] + j[4:7] * dt
    
    # step 3: calculate new accelerations for ALL objects
    Calc_Acc(Objects)

    # step 4: second half-kick, using NEW accel
    for j in Objects:
        j[4:7] = j[4:7] + j[7:10] * (dt/2)

    # save state
    for j in Objects:
        history.append({"t": i, "obj": j[0], "x": j[1], "y": j[2], "z": j[3],
                         "vx": j[4], "vy": j[5], "vz": j[6]})

    i += dt
df = pd.DataFrame(history)
df.to_parquet("sim_output.parquet", index=False)
