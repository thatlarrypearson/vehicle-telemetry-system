# Telemetry Utility Applications

Utility applications supporting [telemetry applications](https://github.com/thatlarrypearson?tab=repositories).

## **UNDER CONSTRUCTION**

## File System Information

Works on Windows 11 and Linux including Raspberry Pi OS.  This application is intended to be used to detect when a specific USB drive is plugged into the Raspberry Pi.

### Usage

```bash
$ python3.11 -m u_tools.file_system_info --help
usage: file_system_info.py [-h] [--match-field MATCH_FIELD]
                           [--match_value MATCH_VALUE]
                           [--print_field PRINT_FIELD] [--verbose] [--version]

Telemetry File System Information

options:
  -h, --help            show this help message and exit
  --match-field MATCH_FIELD
                        Name of the field to match on. Possible field names
                        are: device, volume_label, mount_point,
                        file_system_type, file_system_options.
  --match-value MATCH_VALUE
                        Value to use for matching.
  --print-field PRINT_FIELD
                        The print_field to use when the 'match_field' matches the
                        'match_value'. Default is print all field/value pairs
  --verbose             Print all the information for all disk volumes.
  --version             Print version number and exit.
```

To detect when specific USB drive has been mounted, use ```--match_field```, ```--match_value``` and ```--print_field``` options together as shown in the ```bash``` shell snippet below.

```bash
export VOLUME_LABEL="M2-256"
export MOUNT_POINT="$(python3.11 -m u_tools.file_system_info --match_field volume_label --match_value ${VOLUME_LABEL} --print_field mount_point)"

if [ -n  "${MOUNT_POINT}" ]
then
  echo Match Found mount_point ${MOUNT_POINT} for volume_label ${VOLUME_LABEL}
else
  echo Did not find a match for volume_label ${VOLUME_LABEL}
fi
```

### Output

#### Windows

```bash
$ python3.11 -m u_tools.file_system_info
{'device': 'C:\\', 'volume_label': 'Windows ', 'mount_point': 'C:\\', 'file_system_type': 'NTFS', 'file_system_options': 'rw,fixed'}
{'device': 'D:\\', 'volume_label': 'M2-256', 'mount_point': 'D:\\', 'file_system_type': 'exFAT', 'file_system_options': 'rw,fixed'}
$
```

#### Linux

```bash
$ python3.11 -m u_tools.file_system_info
{'device': '/dev/sdc', 'volume_label': None, 'mount_point': '/', 'file_system_type': 'ext4', 'file_system_options': 'rw,relatime,discard,errors=remount-ro,data=ordered'}
{'device': '/dev/sdc', 'volume_label': None, 'mount_point': '/mnt/wslg/distro', 'file_system_type': 'ext4', 'file_system_options': 'ro,relatime,discard,errors=remount-ro,data=ordered'}
{'device': '/dev/sdc', 'volume_label': None, 'mount_point': '/snap', 'file_system_type': 'ext4', 'file_system_options': 'rw,relatime,discard,errors=remount-ro,data=ordered'}
$
```

#### Raspberry Pi

```bash
$ python3.11 -m u_tools.file_system_info
$
```

## Installation

On Linux, install **Python 3.11** using these [python build instructions](https://github.com/thatlarrypearson/telemetry-obd/blob/master/docs/Python311-Install.md).  On Windows, install **Python 3.11** using the Microsoft Store to get the [Python Software Foundation's Python 3.11](https://www.microsoft.com/store/productId/9NRWMJP3717K?ocid=pdpshare).

## License

This software is licensed under the [MIT software license](LICENSE.md).
