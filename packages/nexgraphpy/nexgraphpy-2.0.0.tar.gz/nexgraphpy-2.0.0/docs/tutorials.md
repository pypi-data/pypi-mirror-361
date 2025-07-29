# Tutorials

## Installation:

`pip install nexgraphpy`

## Examples:

### Import the library:

`from nexgraph import NexGraph`

### Create a new instance:

`DFT_DEVICE = NexGraph()`

### Find and connect to a Nextech force gauge over USB serial port:

```
if DFT_DEVICE.find():
    if DFT_DEVICE.connect():
        print(DFT_DEVICE.get_info())
        DFT_DEVICE.disconnect()
        DFT_DEVICE = None
    else:
        print("Unable to connect")
        exit()
else:
    print("No device found.")
    exit()
```

### Connect to a Nextech force gauge directly:

```
# Initialize with path
DFT_DEVICE = NexGraph("COM3")

# Set the device path after initializing
DFT_DEVICE.device_path = "COM3"

# Connect to device after setting the path
if DFT_DEVICE.connect():
    ...
```

### Basic device serial operations:

#### Returns boolean value
```
# Change device modes, peak and tracking
DFT_DEVICE.mode()

# Change the units on device
DFT_DEVICE.unit()

# Reset the current device value
DFT_DEVICE.reset()

# Zero (Tare) the value on device
DFT_DEVICE.zero()
```

#### Returns string value

##### Download data from device memory
```
# Get data with no formatting
DFT_DEVICE.download()

# Get data in CSV format
DFT_DEVICE.download("csv")

# Get data as bar chart
DFT_DEVICE.download("chart")

# ** Chart is saved in the script directory as "memory-data-yyyymmdd-HHMMSS.png"
```

##### Read and print values from the device

```
# Current value
DFT_DEVICE.print_value()

# Peak compression value
DFT_DEVICE.peak_compression()

# Peak tension value
DFT_DEVICE.peak_tension()

# Different formatted values (Default: "large")
DFT_DEVICE.long_output()
DFT_DEVICE.short_output()
DFT_DEVICE.mini_output()
```

### Output live data of 100 rows:

*Note: 
The output rate is roughly 10 data points per second.
100 data points is approximately 10 seconds of testing.*

```
i = 0
while True:
    print(DFT_DEVICE.long_output())
    i += 1
    if i >= 100:
        break
```
