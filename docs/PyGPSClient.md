# PyGPSClient Installation and Usage

[PyGPSClient](https://github.com/semuconsulting/PyGPSClient), a GUI based GPS testing, diagnostic and UBX © (u-blox ™) device configuration application, is especially useful in debugging [u-blox](https://www.u-blox.com/en) GPS units.

The specific *u-blox* device used in this particular application is [Waveshare](https://www.waveshare.com)'s [NEO-M8T GNSS TIMING HAT for Raspberry Pi, Single-Satellite Timing, Concurrent Reception of GPS, Beidou, Galileo, GLONASS](https://www.waveshare.com/neo-m8t-gnss-timing-hat.htm).

Since installing Python 3.10 from scratch is the recommended approach, the following additional Linux libraries are needed before installing *PyGPSClient* on Raspberry Pi OS (version 11.3 Bullseye):

```bash
sudo apt-get install -y tk-dev
sudo apt-get install -y libjpeg-dev

# Raspberry Pi
sudo apt-get install -y zlib1g-dev
# Ubuntu
# sudo apt-get install -y zlibc

sudo apt-get install -y libtiff-dev
sudo apt-get install -y libfreetype6-dev
sudo apt-get install -y liblcms2-2 liblcms2-dev
sudo apt-get install -y libwebp-dev
sudo apt-get install -y libtk-img-dev
sudo apt-get install -y libopenjp2-7-dev
sudo apt-get install -y libimagequant-dev
sudo apt-get install -y libraqm-dev
sudo apt-get install -y libxcb1-dev
```

The following Python Libraries are needed to finish off the installation:

```bash
python3.10 -m pip install --user --upgrade pyubx2 pynmeagps
python3.10 -m pip install --user --upgrade Pillow
python3.10 -m pip install --user --upgrade pygpsclient

# Test using this command
python3.10 -m pygpsclient
```

## LICENSE

[MIT License](../LICENSE.md)
