import usb.core
import usb.util
import time
import sys

dev = usb.core.find(idVendor=0x04d9, idProduct=0xa09f)

if dev is None:
    raise ValueError("Device not found!")

try:
    dev.reset()
except usb.core.USBError as e:
    print(f"Warning: Could not reset device: {str(e)}")

for config in dev:
    for interface in range(config.bNumInterfaces):
        if dev.is_kernel_driver_active(interface):
            try:
                print(f"Detaching kernel driver from interface {interface}")
                dev.detach_kernel_driver(interface)
            except usb.core.USBError as e:
                print(f"Warning: Could not detach kernel driver: {str(e)}")

try:
    dev.set_configuration()
except usb.core.USBError as e:
    print(f"Warning: Could not set configuration: {str(e)}")

# Get the specific interface you need
i = dev[0].interfaces()[1].bInterfaceNumber

try:
    usb.util.claim_interface(dev, i)
except usb.core.USBError as e:
    # If resource is busy, try to forcefully release it
    if e.errno == 16:
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

data_1 = [0x26, 0x9d, 0x16, 0x98, 0x79, 0xdd, 0x86, 0x36]
bmRequestType_1 = 0x21
bRequest_1 = 0x09
wValue_1 = 0x0300
wIndex_1 = 0x02
wLength_1 = 0x08

def send_control_transfer(data, bmRequestType, bRequest, wValue, wIndex, wLength):
    try:
        dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data)
        print(f"Control transfer sent: {data}")
    except usb.core.USBError as e:
        print(f"Control transfer failed: {str(e)}")

send_control_transfer(data_1, bmRequestType_1, bRequest_1, wValue_1, wIndex_1, wLength_1)

print("Sent off script.")

try:
    usb.util.release_interface(dev, i)
    dev.attach_kernel_driver(i)
except:
    pass
