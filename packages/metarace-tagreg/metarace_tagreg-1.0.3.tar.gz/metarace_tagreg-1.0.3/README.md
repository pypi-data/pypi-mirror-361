# metarace-tagreg

Read transponder ids from a connected decoder.

![tagreg screenshot](screenshot.png "tagreg")

## Requirements

   - Python >= 3.9
   - Gtk >= 3.0
   - metarace >= 2.1.1


## Installation

### Debian 11+

Install system requirements for tagreg and metarace with apt:

	$ sudo apt install python3-venv python3-pip python3-cairo python3-gi python3-gi-cairo
	$ sudo apt install gir1.2-gtk-3.0 gir1.2-rsvg-2.0 gir1.2-pango-1.0
	$ sudo apt install python3-serial python3-paho-mqtt python3-dateutil python3-xlwt

If not already created, add a virtualenv for metarace packages:

	$ mkdir -p ~/Documents/metarace
	$ python3 -m venv --system-site-packages ~/Documents/metarace/venv

Activate the virtualenv and install tagreg with pip:

	$ source ~/Documents/metarace/venv/bin/activate
	(venv) $ pip3 install metarace-tagreg

