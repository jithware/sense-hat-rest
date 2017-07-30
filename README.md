# The Sense HAT Raspberry Pi REST API

This project exposes an REST end point on a [Raspberry Pi Sense HAT](http://amzn.to/2eWl5wz) using python.

Run the following commands on your Raspberry Pi:

To download the source:

`git clone https://github.com/jithware/sense-hat-rest.git`

To build the package:

`makeself ./sense-hat-rest sense-hat-rest.run "Sense HAT Raspberry Pi REST API" ./setup.sh`

Note: if you do not already have makeself installed, run:

`sudo apt-get install makeself`

To install the package, on your Raspberry Pi run:

`sudo ./sense-hat-rest.run`

For usage, navigate to `http://localhost/`

To view live sensor json, navigate to `http://localhost/live/humidity`

You can also view historical sensor graphs by navigating to the html directory `http://localhost/html/humidity`

![humidity](https://raw.githubusercontent.com/jithware/sense-hat-rest/master/images/humidity.png)
