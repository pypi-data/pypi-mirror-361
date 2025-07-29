<h1 align="center">
<img src="https://python.nexgraphapp.com/assets/images/nexgraph-logo-wide.png">
</h1><br />

# Nexgraph Python

## Description:
NexGraph Python is a Python library implementation of the [NexGraph](https://nexgraphapp.com) software which works with Nextech brand DFT and DFS force gauges.  It connects to the force gauge over USB serial and enables you to operate your device using Python. Download data from your devices, execute commands, and read data.  Device Memory data can be output in CSV format or a bar chart.

## Requirements:
Tested on Python versions 3.10+

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
# Initialize with device the path
DFT_DEVICE = NexGraph("COM3")

# Or set the device path after initializing
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

# ** Chart is saved in the script directory as "memory-data-yyyy-mm-dd-HH:MM:SS.png"
```

##### Read and print values from the device

```
# Print value
DFT_DEVICE.print_value()

# Peak compression value
DFT_DEVICE.peak_compression()

# Peak tension value
DFT_DEVICE.peak_tension()

# Different formatted values
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
## Documentation

[Nexgraph Python Docs](https://python.nexgraphapp.com/)
<https://python.nexgraphapp.com/>

## NexGraph Desktop Application
The latest version of the NexGraph desktop application with features such as live graphing, and pass/fail data highlighting is available now for Windows.
Get it from: <https://nexgraphapp.com>.