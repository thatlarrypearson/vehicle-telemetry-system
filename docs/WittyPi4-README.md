# Witty Pi 4 Telemetry Support Programs

UUGear's [Witty Pi 4 Realtime Clock and Power Management HAT](https://www.uugear.com/product/witty-pi-4/) for Raspberry Pi 4B is provided with configuration software to

* synchronize Real Time Clock (RTC) with Network Time
* set recovery voltage threshold

These functions must be present after the network is initialized and before other telemetry apps start.

Linux ```bash``` shell programs included in this repo provide the necessary instructions to perform Witty Pi 4 Configuration.

## **UNDER CONSTRUCTION**

## Installation

### Enable I2C Support

Enable ```i2c``` support using ```raspi-config``` as shown below.

![Interface Options](docs/i2c-01.png)

![I2C](docs/i2c-02.png)

![Enable I2C?](docs/i2c-03.png)

![OK, I2C Enabled](docs/i2c-04.png)

![Finish](docs/i2c-05.png)

### Install Witty Pi 4

Follow the software installation instructions found in the [Witty Pi 4 User Manual](https://www.uugear.com/doc/WittyPi4_UserManual.pdf) before continuing.

### Download Repo

```bash
cd
git clone https://github.com/thatlarrypearson/telemetry-WittyPi4.git
```

### Customize

Edit ```telemetry-WittyPi4/root/bin/telemetry.rc.local.wittypi4```

* Change ```export WITTYPI4_USER="lbp"``` to ```export WITTYPI4_USER="```**<your-**```user-name```**-goes-here>**```"```.

The current ```user-name``` is displayed by the ```whoami``` command.

```bash
lbp@telemetry2:~ $ whoami
lbp
lbp@telemetry2:~ $
```

### Finish Install

```bash
cd
cd telemetry-WittyPi4
chmod 0755 bin/boot_config.sh
sudo mkdir  /root/bin
sudo cp root/bin/telemetry.rc.local.wittypi4.sh /root/bin/
sudo chown root /root/bin/telemetry.rc.local.wittypi4
sudo chmod 0755 /root/bin/telemetry.rc.local.wittypi4
```

### Test Base Install

```bash
sudo bash /root/bin/telemetry.rc.local.wittypi4
```

Test results are in the most recent ```wittypi4``` log file in ```/root/tmp/```.  Log files are generated every time ```/root/bin/telemetry.rc.local.wittypi4``` is executed.

```ls -tr telemetry-wittypi4_*``` returns a matching file list in reverse date/time order.  That is, the newest file is last in the list.  ```tail -n 1```  prints the last line, the newest file.   ```cat``` prints out the file.

```bash
sudo -i
cat $(ls -tr /root/tmp/telemetry-wittypi4_* | tail -n 1)
exit
```

Example:

```bash
lbp@telemetry2:~ $ sudo -i
root@telemetry2:~# cat $(ls -tr /root/tmp/telemetry-wittypi4_* | tail -n 1)
+ sleep 60
+ runuser -u lbp -g i2c /home/lbp/telemetry-WittyPi4/bin/boot_config.sh
  Applying network time to system...
  Done :-)
  Writing system time to RTC...
  Done :-)
Set to "Default ON"!
root@telemetry2:~# exit
logout
lbp@telemetry2:~ $
```

### Start On Boot

The Witty Pi 4 configuration software needs to start during the boot process.  To prepare for running on boot, modify the ```/etc/rc.local``` file.

To start the Witty Pi 4 configuration software at boot on a Raspberry Pi, add the section of code starting with ```# BEGIN TELEMETRY-WITTYPI4 SUPPORT``` and ending with ```# END TELEMETRY-WITTYPI4 SUPPORT``` to ```/etc/rc.local```.

An example  ```/etc/rc.local``` file is provided at ```telemetry-WittyPi4/etc/rc.local```.

```bash
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

# BEGIN TELEMETRY-WTHR SUPPORT
# This section goes before the TELEMETRY_OBD section

if [ -x "/root/bin/telemetry.rc.local.wthr" ]
then
    /bin/nohup "/root/bin/telemetry.rc.local.wthr" &
fi

# END TELEMETRY-WTHR SUPPORT

# BEGIN TELEMETRY-GPS SUPPORT
# This section goes before the TELEMETRY_OBD section

if [ -x "/root/bin/telemetry.rc.local.gps" ]
then
    /bin/nohup "/root/bin/telemetry.rc.local.gps" &
fi

# END TELEMETRY-GPS SUPPORT

# BEGIN TELEMETRY-OBD SUPPORT

if [ -x "/root/bin/telemetry.rc.local" ]
then
    /bin/nohup "/root/bin/telemetry.rc.local" &
fi

# END TELEMETRY-OBD SUPPORT

# BEGIN TELEMETRY-WITTYPI4 SUPPORT
# This section goes last

if [ -x "/root/bin/telemetry.rc.local.wittypi4" ]
then
    /bin/nohup "/root/bin/telemetry.rc.local.wittypi4" &
fi

# END TELEMETRY-WITTYPI4 SUPPORT

exit 0
```

## License

[MIT](LICENSE.md)
