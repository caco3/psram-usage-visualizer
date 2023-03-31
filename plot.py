import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import argparse

divisions = 256


parser = argparse.ArgumentParser()
parser.add_argument('csvfile', help='PSRAM usage table (*.csv)', type=argparse.FileType('r'))

args = parser.parse_args()


data = np.genfromtxt(args.csvfile.name, delimiter=",")

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "red", "mistyrose", "darkgreen"])


plt.imshow(data, cmap=cmap, aspect="auto")


plt.grid(True)

plt.yticks(np.arange(0, divisions, divisions/4), np.arange(0, 4, 16*divisions/4096))
plt.ylabel('PSRAM in MBytes')
plt.xlabel('Malloc/free actions')

plt.show()