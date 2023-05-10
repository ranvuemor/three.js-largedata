import json
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from  mpl_toolkits.mplot3d import Axes3D
import math

# open netcdf file
nc_file = Dataset("./Temperature4Dsubset.nc")

# get variable arrays
# red = nc_file.variables["red"][:]
# green = nc_file.variables["green"][:]
# blue = nc_file.variables["blue"][:]
# elev = np.array(nc_file.variables["elev"][:])
# lat = np.array(nc_file.variables["Lat"][:])
# lon = np.array(nc_file.variables["Lon"][:])

# create a list of dictionaries with grouped data
# data_list = []
# for i, e in enumerate(elev):
#     for j, ln in enumerate(lon):
#         for k, lt in enumerate(lat):
#             data_dict = {
#                 "elevation": float(e),
#                 "lon": float(ln),
#                 "lat": float(lt),
#                 "red": float(red[i][j][k]),
#                 "green": float(green[i][j][k]),
#                 "blue": float(blue[i][j][k]),
#             }
#             print(data_dict)
#             data_list.append(data_dict)

#print(len(elev), len(lat), len(lon), len(red))

# for i in range(len(elev)):
#     for j in range(len(lon)):
#         for k in range(len(lat)):
#             data_dict = {
#                 "elevation": float(elev[i]),
#                 "lon": float(lon[j]),
#                 "lat": float(lat[k]),
#                 "red": float(red[i][j][k]),
#                 "green": float(green[i][j][k]),
#                 "blue": float(blue[i][j][k]),
#             }

# write data to json file
# with open("output.json", "w") as outfile:
#     json.dump(data_list, outfile)



# def f(x, y):
#     return np.sin(np.sqrt(x ** 2 + y ** 2))

# x = np.linspace(-179.95, -160.05, 200)
# y = np.linspace(89.95, 70.05, 200)

# lonc, latc = np.meshgrid(x, y)

# elevc = f(lonc, latc)
# red_norm = red.reshape(-1).astype(float) / 255.0
# green_norm = green.reshape(-1).astype(float) / 255.0
# blue_norm = blue.reshape(-1).astype(float) / 255.0

# #rgb_array = np.column_stack(red_norm, green_norm, blue_norm)


# fig = plt.figure()

# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(lonc, latc, elevc, c=np.column_stack(red_norm, green_norm, blue_norm), s=0.1)

# ax.set_xlabel('Latitude')
# ax.set_ylabel('Longitude')
# ax.set_zlabel('Elevation')

# plt.show()

elev = nc_file.variables["elev"][:]
lat = nc_file.variables["Lat"][:]
lon = nc_file.variables["Lon"][:]
red = nc_file.variables["red"][:].flatten()
green = nc_file.variables["green"][:].flatten()
blue = nc_file.variables["blue"][:].flatten()

# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
count = 0

# Plot the points with colors based on RGB values
for k in range(int(len(elev))):
    for i in range(int(len(lon)/5)):
        for j in range(int(len(lat)/5)):
            r = 6371
            x = lat[j*5]
            y = lon[i*5]
            z = elev[k]
            x1 = r * math.cos(x) * math.cos(y)
            y1 = r * math.cos(x) * math.sin(y)
            if (x >= 0):
                z1 = r * math.sin(x) + z
            else:
                z1 = -(r * math.sin(x) + z)
            
            r = red[(i * len(lon) + j)*5] / 255.0
            g = green[(i * len(lon) + j)*5] / 255.0
            b = blue[(i * len(lon) + j)*5] / 255.0
            if (r != 0 and g != 0 and b != 0):
                count += 1
                print(x1, z1, y1, r, g, b)
                #ax.scatter(x1, z1, y1, c=(r, g, b))

print(count)
# Set labels and title
for i in range(20):
    for k in range(20):
        ax.scatter(i-10, k-10, 10)

ax.set_xlabel("x")
ax.set_zlabel("z")
ax.set_ylabel("y")
ax.set_title("3D Scatter Plot of Elevation Data")

plt.show()


