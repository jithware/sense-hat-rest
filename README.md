# The Sense HAT Raspberry Pi REST API

This project exposes a REST end point on a [Raspberry Pi Sense HAT](https://www.raspberrypi.org/products/sense-hat/) using python.

Run the following commands on your Raspberry Pi with a Sense HAT:

To download the source:

```sh
git clone https://github.com/jithware/sense-hat-rest.git
```

To install:

```sh
sudo ./setup.sh
```

To build the package (optional):

```sh
makeself ./sense-hat-rest sense-hat-rest.run "Sense HAT Raspberry Pi REST API" ./setup.sh
```

Note: if you do not already have makeself installed:

```sh
sudo apt-get install makeself
```

To install the package:

```sh
sudo ./sense-hat-rest.run
```

For usage, navigate to `http://localhost/`

To get live sensor json, navigate to the live directory `http://localhost/live/temperature`

```json
{"temperature": 25.48150062561035}
```

To view historical sensor data, navigate to the html directory `http://localhost/html/temperature`

![temperature](./images/temperature.png)

To trigger an IFTTT event, create a webhook applet at [ifttt.com](https://ifttt.com/create/if-maker_webhooks) with a sense_hat event and update [sense-hat-rest.conf](./sense-hat-rest.conf) with your key and sensor values: 
```
[notify]

IFTTTKEY=
MINTEMP=
MAXTEMP=
```
