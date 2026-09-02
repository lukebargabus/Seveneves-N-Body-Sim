import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("sim_output.parquet")

plt.figure(figsize=(6, 6))
for obj_mass, group in df.groupby("obj"):
    plt.plot(group["x"], group["y"], marker="o", markersize=2, label=f"mass={obj_mass}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Earth-Moon trajectories")
plt.axis("equal")
plt.legend()
plt.savefig("sim_plot.png", dpi=150)
plt.show()