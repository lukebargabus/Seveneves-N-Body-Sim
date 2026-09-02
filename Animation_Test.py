import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


df = pd.read_parquet("sim_output.parquet")
num_timesteps = df["t"].nunique()

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

x_min, x_max = df["x"].min(), df["x"].max()
y_min, y_max = df["y"].min(), df["y"].max()
z_min, z_max = -1,1



def update(i):
    ax.clear()
    frame_df = df[df["t"] == i]
    for obj_mass, group in frame_df.groupby("obj"):
        ax.scatter(group["x"], group["y"], group["z"], s=20, label=f"mass={obj_mass}")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Earth-Moon trajectories")
    ax.legend()


ani = FuncAnimation(fig, update, frames=sorted(df["t"].unique()), interval=50)

ani.save('orbit.gif', writer='pillow')
plt.show()
