import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import math
import argparse

divisions = 256


parser = argparse.ArgumentParser()
parser.add_argument('csvfile', help='PSRAM usage table (*.csv)', type=argparse.FileType('r'))

args = parser.parse_args()


data = np.genfromtxt(args.csvfile.name, delimiter=",")

# Line 1 = line number in log file
logLineNumbers = data[0]
data = data[1:]

# Line 2 = Malloc size in Bytes
mallocSize = data[0]
data = data[1:]


cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white", "red", "mistyrose", "darkgreen"])


plt.imshow(data, cmap=cmap, aspect="auto")
plt.grid(True)
#plt.grid(False)

xDivider = math.floor(len(logLineNumbers)/40)
#xDivider = 1

xticks = np.arange(0, len(logLineNumbers))
plt.yticks(np.arange(0, divisions, divisions/4), np.arange(0, 4, 16*divisions/4096))
plt.xticks(xticks[0::xDivider], [int(x) for x in logLineNumbers[0::xDivider]], rotation = 90)

plt.ylabel('PSRAM in MBytes')
plt.xlabel('Logfile Line of Malloc/free actions')

plt.show()