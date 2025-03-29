# telemetry-usb/usb_tools/usb_devices.py
#
# Works on Linux (maybe Mac) and Windows.
# python3.11 -m pip install psutil
# Only works on Linux, not needed on Windows.
# python3.11 -m pip install diskinfo

import psutil
import ctypes
import platform
from os import getlogin
from argparse import ArgumentParser
from .__init__ import __version__

FIELD_LIST = [
    'device',
    'volume_label',
    'mount_point',
    'file_system_type', 
    'file_system_options'
]

system_type = platform.system()

if system_type == 'Windows':
    def get_volume_label(partition)->str:
        """
        Return drive 'volume_label' given
        'partition' in the following format: "F:\\" (single trailing slash)
        """
        kernel32 = ctypes.windll.kernel32
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        serial_number = None
        max_component_length = None
        file_system_flags = None

        rc = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(partition.device),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            serial_number,
            max_component_length,
            file_system_flags,
            fileSystemNameBuffer,
            ctypes.sizeof(fileSystemNameBuffer)
        )

        return volumeNameBuffer.value

elif system_type == 'Linux':
    import subprocess

    def get_volume_label(partition):
        try:
            result = subprocess.run(['blkid', '-o', 'value', '-s', 'LABEL', partition.device], capture_output=True, text=True, check=True)
            if blkid_output := result.stdout.strip():
                return blkid_output
            else:
                # 'mount_point': "/media/{USER}/{LABEL}"
                user_name = getlogin()
                if partition.mountpoint.startswith(f"/media/{user_name}"):
                    return (partition.mountpoint.split('/'))[3]
        except Exception:
            pass
        return None

else:
    raise OSError("Unsupported Operating System Type '{system_type}'")

# File System Mount Points
def get_file_system_mount_points()->list:
    """
    returns a list of file systems where each file system is represented as
    a dictionary.
    Windows:
        [
            {
                'device': 'C:\\',
                'volume_label': 'Windows ',
                'mount_point': 'C:\\', 
                'file_system_type': 'NTFS', 
                'file_system_options': 'rw,fixed'
            },
        ]
    Linux:
        [
            {
                'device': '/dev/mmcblk0p2', 
                'volume_label': 'rootfs', 
                'mount_point': '/', 
                'file_system_type': 'ext4', 
                'file_system_options': 'rw,noatime'
            },
            {
                'device': '/dev/mmcblk0p1', 
                'volume_label': 'bootfs', 
                'mount_point': '/boot/firmware', 
                'file_system_type': 'vfat', 
                'file_system_options': 'rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,errors=remount-ro'
            },
            {
                'device': '/dev/sda1', 
                'volume_label': 'M2-256', 
                'mount_point': '/media/lbp/M2-256', 
                'file_system_type': 'exfat', 
                'file_system_options': 'rw,nosuid,nodev,relatime,uid=1000,gid=1000,fmask=0022,dmask=0022,iocharset=utf8,errors=remount-ro'
            }
        ]
    """
    mount_points = []
    for partition in psutil.disk_partitions():
        try:
            volume_label = get_volume_label(partition)
        except Exception:
            volume_label = None

        mount_points.append(
            {
                'device': partition.device,
                'volume_label': volume_label,
                'mount_point': partition.mountpoint,
                'file_system_type': partition.fstype,
                'file_system_options': partition.opts,
            }
        )

    return mount_points

def argument_parsing()-> dict:
    """Command line argument parsing"""
    parser = ArgumentParser(description="Telemetry File System Information")

    parser.add_argument(
        "--match_field",
        default=None,
        help=f"Name of the field to match on. Possible field names are: {', '.join(FIELD_LIST)}.",
    )

    parser.add_argument(
        "--match_value",
        default=None,
        help="Value to use for matching."
    )

    parser.add_argument(
        "--print_field",
        default=None,
       help="The field to print when the 'match_field' matches the 'match_value'.  Default is print all field/value pairs",
    )

    parser.add_argument(
        "--verbose",
        default=False,
        action='store_true',
        help="Print all the information for all disk volumes."
    )

    parser.add_argument(
        "--version",
        default=False,
        action='store_true',
        help="Print version number and exit."
    )

    return vars(parser.parse_args())

def main():
    args = argument_parsing()

    if args['version']:
        print(f"Version {__version__}")
        exit(0)

    verbose = args['verbose']
    match_field = args['match_field']
    if match_field and match_field not in FIELD_LIST:
        print("Invalid --match_field argument: {match_field} not in {FIELD_LIST}")
        exit(1)

    match_value = args['match_value']
    if match_value and not match_field:
        print("match_field requires match_value")
        exit(1)

    print_field = args['print_field']
    if print_field and print_field not in FIELD_LIST:
        print("Invalid --print_field argument: {print_field} not in {FIELD_LIST}")
        exit(1)

    mount_points = get_file_system_mount_points()
    for mount_point in mount_points:
        if verbose or (not match_field and not print_field):
            print(f"{mount_point}")
        if print_field and not match_field:
            print(mount_point[print_field])
        if match_field and match_value and mount_point[match_field] == match_value:
            if print_field:
                print(mount_point[print_field])
            else:
                print(f"{mount_point}")

if __name__ == "__main__":
    main()

