# Bluetooth Installation and Configuration

OBD II adapters are devices that attach to vehicle OBD II ports allowing a computer to query vehicle On-Board Diagnostic capabilities.  Bluetooth is the recommended method to connect an OBD II adapter the [Raspberry Pi Data Collector](./README-rpdc.md).  These instructions cover the installation and configuration of [Raspberry Pi Data Collector](./README-rpdc.md) Bluetooth software enabling communication between the [Raspberry Pi Data Collector](./README-rpdc.md) and a Bluetooth OBD II adapter.

## **UNDER CONSTRUCTION**

## Install System Software

On Linux/Raspberry Pi systems install the Bluetooth support software and then reboot the system:

```bash
# Bluetooth support software
sudo apt-get install -y bluetooth bluez bluez-tools blueman bluez-hcidump
# Bluetooth support software requires reboot to become activated
sudo shutdown -r now
```

## Pairing Bluetooth OBD Devices

Bluetooth OBD adapters must be *paired* and *trusted* before they can be used.  The *pairing* and *trust* process is covered in [Pairing Bluetooth OBD Devices](./docs/README-BluetoothPairing.md).

## Bluetooth Trouble

After operating system upgrades, Bluetooth may not operate as expected.  Possible solutions may include

- Completely un-pair/remove OBD adapter from Bluetooth configuration followed by a reboot.  Next, boot the system and follow the [Bluetooth pairing instructions](./docs/README-BluetoothPairing.md).
- Follow instructions in [Use app to connect to pi via bluetooth](https://forums.raspberrypi.com/viewtopic.php?p=947185#p947185).

## Bluetooth Configuration

On Windows 10, connecting to USB or Bluetooth ELM 327 OBD interfaces is simple.  Plug in the USB and it works.  Pair the Bluetooth ELM 327 OBD interface and it works.  Linux and Raspberry Pi systems are a bit more challenging.

The first step is to pair the [Raspberry Pi Data Collector](./README-rpdc.md) to the Bluetooth OBD adapter.  One easy way to pair is to use the Raspberry Pi's GUI to access Bluetooth.  The *pairing* and *trust* process is covered in [Pairing Bluetooth OBD Devices](./docs/README-BluetoothPairing.md).

![RaspberryPi Bluetooth GUI Utility](docs/README-rpi-gui-bt.jpg)

Once the OBD adapter has been paired, continue with the following.

On Linux/Raspberry Pi based systems, USB ELM 327 based OBD interfaces present as ```tty``` devices (e.g. ```/dev/ttyUSB0```).  If software reports that the OBD interface can't be accessed, the problem may be one of permissions.  Typically, ```tty``` devices are owned by ```root``` and group is set to ```dialout```.  The user that is running the OBD data capture program must be a member of the same group (e.g. ```dialout```) as the ```tty``` device.

```bash
# add dialout group to the current user's capabilities
sudo adduser $(whoami) dialout
```

On Linux/Raspberry Pi, Bluetooth serial device creation is not automatic.  After Bluetooth ELM 327 OBD interface has been paired, ```sudo rfcomm bind rfcomm0 <BT-MAC-ADDRESS>``` will create the required serial device.   An example follows:

```bash
# get the Bluetooth ELM 327 OBD interface's MAC (Media Access Control) address
sudo bluetoothctl
[bluetooth]# devices
Device 00:00:00:33:33:33 OBDII
[bluetooth]# exit
# MAC Address for OBD is "00:00:00:33:33:33"

# bind the Bluetooth ELM 327 OBD interface to a serial port/device using the interfaces Bluetooth MAC (Media Access Control) address:
sudo rfcomm bind rfcomm0 00:00:00:33:33:33
```

On Linux/Raspberry Pi systems, the ```rfcomm``` command creates the device ```/dev/rfcomm0``` as a serial device owned by  ```root``` and group ```dialout```.  If multiple Bluetooth serial devices are paired and bound to ```/dev/rfcomm0```, ```/dev/rfcomm1```, ```/dev/rfcomm2``` and so on, OBD Logger will only automatically connect to the first device.  The code can be modified to resolve this limitation.

Regardless of connection type (USB or Bluetooth) to an ELM 327 OBD interface, the serial device will be owned by ```root``` with group ```dialout```.  Access to the device is limited to ```root``` and users in the group ```dialout```.

Users need to be added to the group ```dialout```.  Assuming the user's username is ```human```:

```bash
human@hostname:~ $ ls -l /dev/ttyUSB0
crw-rw---- 1 root dialout 188, 0 Aug 13 15:47 /dev/ttyUSB0
human@hostname:~ $ ls -l /dev/rfcomm0
crw-rw---- 1 root dialout 120, 0 Aug 13 15:47 /dev/rfcomm0
human@hostname:~ $ sudo adduser human dialout
```

## Manufacturer Warranty Information

The 2019 Ford EcoSport manual and other vehicles have the following statement or something similar with respect to aftermarket OBD devices:

- "Your vehicle has an OBD Data Link Connector (DLC) that is used in conjunction with a diagnostic scan tool for vehicle diagnostics, repairs and reprogramming services. Installing an aftermarket device that uses the DLC during normal driving for purposes such as remote insurance company monitoring, transmission of vehicle data to other devices or entities, or altering the performance of the vehicle, may cause interference with or even damage to vehicle systems. We do not recommend or endorse the use of aftermarket plug-in devices unless approved by Ford. The vehicle Warranty will not cover damage caused by an aftermarket plug-in device."

You use this software at your own risk.

## LICENSE

[MIT License](./LICENSE.md)
