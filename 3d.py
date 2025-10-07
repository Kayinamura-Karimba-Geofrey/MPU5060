import sys
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
import numpy as np

# ----- CONFIG -----
BAUD = 115200

# ----- AUTO-DETECT ARDUINO COM PORT -----
ports = list(serial.tools.list_ports.comports())
arduino_port = None
for p in ports:
    if "Arduino" in p.description or "CH340" in p.description:
        arduino_port = p.device
        break

if arduino_port is None:
    print("Arduino not found! Available ports:")
    for p in ports:
        print(p.device, p.description)
    sys.exit(1)

print("Using Arduino on port:", arduino_port)
PORT = arduino_port
ser = serial.Serial(PORT, BAUD, timeout=1)

# ----- FIGURE SETUP -----
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-2, 2])
ax.set_ylim([-2, 2])
ax.set_zlim([0, 4])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Cup Tilt (Pitch=Blue, Roll=Green, Yaw=Red)')

# ----- CREATE CUP -----
def create_cup(radius=1.0, height=3.0, resolution=30):
    theta = np.linspace(0, 2*np.pi, resolution)
    z = np.linspace(0, height, 2)
    theta, z = np.meshgrid(theta, z)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x, y, z

cup_x, cup_y, cup_z = create_cup()
cup_surf = ax.plot_surface(cup_x, cup_y, cup_z, color='orange', alpha=0.8)

# ----- HELPER -----
def parse_line(line):
    try:
        parts = line.strip().split(',')
        if len(parts) != 3:
            return None, None, None
        pitch = float(parts[0])
        roll  = float(parts[1])
        yaw   = float(parts[2])
        return pitch, roll, yaw
    except:
        return None, None, None

def rotation_matrix(roll_deg, pitch_deg, yaw_deg):
    r = np.radians(roll_deg)
    p = np.radians(pitch_deg)
    y = np.radians(yaw_deg)

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(r), -np.sin(r)],
                   [0, np.sin(r),  np.cos(r)]])
    
    Ry = np.array([[np.cos(p), 0, np.sin(p)],
                   [0, 1, 0],
                   [-np.sin(p),0,np.cos(p)]])
    
    Rz = np.array([[np.cos(y), -np.sin(y), 0],
                   [np.sin(y),  np.cos(y), 0],
                   [0, 0, 1]])
    
    return Rz @ Ry @ Rx

# ----- ANIMATION FUNCTION -----
def update(frame):
    global cup_surf
    cup_surf.remove()
    
    # Read latest data
    for _ in range(5):
        raw = ser.readline().decode(errors='ignore')
        if not raw:
            continue
        pitch, roll, yaw = parse_line(raw)
        if pitch is None:
            continue
        break
    else:
        pitch, roll, yaw = 0, 0, 0
    
    # Flatten and rotate
    points = np.vstack((cup_x.flatten(), cup_y.flatten(), cup_z.flatten()))
    R = rotation_matrix(roll, pitch, yaw)
    rotated = R @ points
    x_r = rotated[0].reshape(cup_x.shape)
    y_r = rotated[1].reshape(cup_y.shape)
    z_r = rotated[2].reshape(cup_z.shape)

    # Pick color based on largest angle
    abs_vals = [abs(pitch), abs(roll), abs(yaw)]
    max_idx = abs_vals.index(max(abs_vals))
    if max_idx == 0:
        color = 'blue'   # Pitch
    elif max_idx == 1:
        color = 'green'  # Roll
    else:
        color = 'red'    # Yaw

    # Draw rotated cup
    cup_surf = ax.plot_surface(x_r, y_r, z_r, color=color, alpha=0.8)
    return cup_surf,

# ----- RUN ANIMATION -----
ani = animation.FuncAnimation(fig, update, interval=30, blit=False, cache_frame_data=False)
plt.show()
