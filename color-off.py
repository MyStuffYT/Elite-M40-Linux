import usb.core
import usb.util
import time
import sys

# Find the USB device
dev = usb.core.find(idVendor=0x04d9, idProduct=0xa09f)

if dev is None:
    raise ValueError("Device not found!")

# Reset the device first
try:
    dev.reset()
except usb.core.USBError as e:
    print(f"Warning: Could not reset device: {str(e)}")

# Detach kernel driver from all interfaces if active
for config in dev:
    for interface in range(config.bNumInterfaces):
        if dev.is_kernel_driver_active(interface):
            try:
                print(f"Detaching kernel driver from interface {interface}")
                dev.detach_kernel_driver(interface)
            except usb.core.USBError as e:
                print(f"Warning: Could not detach kernel driver: {str(e)}")

# Set configuration
try:
    dev.set_configuration()
except usb.core.USBError as e:
    print(f"Warning: Could not set configuration: {str(e)}")

# Get the specific interface you need
i = dev[0].interfaces()[1].bInterfaceNumber

# Claim the interface
try:
    usb.util.claim_interface(dev, i)
except usb.core.USBError as e:
    # If resource is busy, try to forcefully release it
    if e.errno == 16:  # Resource busy
        print("Device busy. Attempting to force release...")
        # On Linux, you can try this:
        # import os
        # os.system(f"sudo sh -c 'echo {hex(dev.idVendor)} {hex(dev.idProduct)} > /sys/bus/usb/drivers/usb/unbind'")
        # Alternative approach: force a reset
        try:
            dev.reset()
            time.sleep(1)  # Give device time to reset
            # Try again
            usb.util.claim_interface(dev, i)
        except:
            sys.exit("Could not claim interface even after reset. Device might be in use by another program.")
    else:
        sys.exit(f"Could not claim interface {i}: {str(e)}")

# Define your data and parameters
# OFF = [0x26, 0x9c, 0xfe, 0x98, 0x79, 0xb5, 0x86, 0x76]
data_1 = [0x26, 0x9c, 0xfe, 0x98, 0x79, 0xb5, 0x86, 0x76]
bmRequestType_1 = 0x21
bRequest_1 = 0x09
wValue_1 = 0x0300
wIndex_1 = 0x02
wLength_1 = 0x08

data_2 = [0x26, 0x9d, 0x16, 0x98, 0x79, 0xdd, 0x86, 0x36]
bmRequestType_2 = 0x21
bRequest_2 = 0x09
wValue_2 = 0x0300
wIndex_2 = 0x02
wLength_2 = 0x08

data_3 = [0x26, 0x9d, 0x16, 0x98, 0x79, 0xdd, 0x86, 0x36]
bmRequestType_3 = 0x21
bRequest_3 = 0x09
wValue_3 = 0x0300
wIndex_3 = 0x02
wLength_3 = 0x08

# Function to send control transfer
def send_control_transfer(data, bmRequestType, bRequest, wValue, wIndex, wLength):
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data)
        print(f"Control transfer sent: {data}")
    except usb.core.USBError as e:
        print(f"Control transfer failed: {str(e)}")

# Replay each frame's control transfer
send_control_transfer(data_1, bmRequestType_1, bRequest_1, wValue_1, wIndex_1, wLength_1)
time.sleep(0.1)  # Small delay between requests

#send_control_transfer(data_2, bmRequestType_2, bRequest_2, wValue_2, wIndex_2, wLength_2)
time.sleep(0.1)  # Small delay between requests

#send_control_transfer(data_3, bmRequestType_3, bRequest_3, wValue_3, wIndex_3, wLength_3)
print("All control transfers sent!")

# Always release the interface when done
try:
    usb.util.release_interface(dev, i)
    # Optional: reattach the kernel driver
    dev.attach_kernel_driver(i)
except:
    pass
