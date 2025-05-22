import matplotlib.pyplot as plt
from utility import read_txt
import numpy as np


def setCoords(file1, file2):
        
        x_points = read_txt(file1)
        y_points = read_txt(file2)
        coords = []

        for i, x in enumerate(x_points):
            coords.append([x, y_points[i]])

        return np.array(coords)


coords = setCoords("GetX.TXT", "GetY.TXT")


x = []
y = round(coords[0][1])
subset = []
for p in coords:
    
    if y != round(p[1]):
        print(y)
        x.append(subset.copy())
        y = round(p[1])
        subset.clear()

    subset.append(p[1])

x.append(subset)

print(x)

fig, axes = plt.subplots(len(x), 1, figsize=(6,8), sharex=True)

for i, e in enumerate(x):
    print(e)
    axes[i].plot(e, marker="o", label=f"Row {i}")
    axes[i].set_ylim(min(e), max(e))
    axes[i].set_ylabel("Value")
    axes[i].legend(loc="upper right")
    axes[i].grid(True)
   

axes[-1].set_xlabel("COlumn Index")
plt.suptitle("Each row", fontsize=14)
plt.tight_layout(rect=[0,0,1,0.96])
plt.show()




