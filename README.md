# The Sense HAT Raspberry Pi REST API

This project exposes a REST end point on a [Raspberry Pi](https://www.raspberrypi.com/) equiped with a [Sense HAT](https://www.raspberrypi.org/products/sense-hat/).

The following commands are run on your Raspberry Pi:

## Install from release
```sh
curl -sSL https://github.com/jithware/sense-hat-rest/releases/latest/download/sense-hat-rest.run -o sense-hat-rest.run 
chmod +x sense-hat-rest.run
./sense-hat-rest.run 
```

## Install from git

```sh
git clone https://github.com/jithware/sense-hat-rest.git
cd sense-hat-rest
./setup.sh
```

## Usage

For full api documentation, navigate to the sense-hat-rest [port](https://github.com/jithware/sense-hat-rest/blob/master/sense-hat-rest.service#L6) on your Raspberry Pi: `http://raspberrypi:8080/` 

### Examples
To get live temperature sensor json, navigate to the live directory: `http://raspberrypi:8080/live/temperature`

```json
{"temperature": 25.48150062561035}
```

To view historical temperature sensor data, navigate to the html directory: `http://raspberrypi:8080/html/temperature`

![temperature](./images/temperature.png)

### IFTTT event

To trigger an IFTTT temperature event, create a webhook applet at [ifttt.com](https://ifttt.com/create/if-maker_webhooks) with a sense_hat event and update [sense-hat-rest.conf](./sense-hat-rest.conf) with your key and sensor values: 
```
[notify]

IFTTTKEY=
MINTEMP=
MAXTEMP=
```

## Debug

To debug issues, run [sense-hat-rest.py](./sense-hat-rest.py) from the command line:
```sh
sense-hat-rest.py
```
