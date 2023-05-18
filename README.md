# The Sense HAT Raspberry Pi REST API

This project exposes a REST end point on a [Raspberry Pi Sense HAT](https://www.raspberrypi.org/products/sense-hat/) using python.

Run the following commands on your Raspberry Pi with a Sense HAT:

## Install from release package
```sh
curl -sSL https://github.com/jithware/sense-hat-rest/releases/latest/download/sense-hat-rest.run -o sense-hat-rest.run 
chmod +x sense-hat-rest.run
sudo ./sense-hat-rest.run 
```

## Install from git

```sh
git clone https://github.com/jithware/sense-hat-rest.git
cd sense-hat-rest
sudo ./setup.sh
```

## Build the package (optional):

```sh
sudo apt-get install makeself
makeself --tar-extra "--exclude=.git* --exclude=images" ./ sense-hat-rest.run "Sense HAT Raspberry Pi REST API" ./setup.sh
```

## Usage

For api the definitions, navigate to `http://localhost:8080/` 

To get live sensor json, navigate to the live directory `http://localhost:8080/live/temperature`

```json
{"temperature": 25.48150062561035}
```

To view historical sensor data, navigate to the html directory `http://localhost:8080/html/temperature`

![temperature](./images/temperature.png)

## IFTTT Event

To trigger an IFTTT event, create a webhook applet at [ifttt.com](https://ifttt.com/create/if-maker_webhooks) with a sense_hat event and update [sense-hat-rest.conf](./sense-hat-rest.conf) with your key and sensor values: 
```
[notify]

IFTTTKEY=
MINTEMP=
MAXTEMP=
```
