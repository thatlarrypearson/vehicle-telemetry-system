# boot.py
import usb_cdc

# disable both serial devices
usb_cdc.disable()

# re-enable each serial devices
# we want to enable data=True but gets
# the following message:
# You are in safe mode because:
# USB devices need more endpoints than are available.
# Press reset to exit safe mode.
usb_cdc.enable(console=True, data=False)
