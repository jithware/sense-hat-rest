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
To retrieve live temperature json, GET temperature from the live directory: `http://raspberrypi:8080/live/temperature`

```sh
curl -s http://raspberrypi:8080/live/temperature
{"temperature": 16.162643432617188}
```

To retrieve historical temperature json, GET temperature from the past directory: `http://raspberrypi:8080/past/temperature`

```sh
curl -s http://raspberrypi:8080/past/temperature?start=10m
{"meta": {"start": 1684696560, "end": 1684697220, "step": 60, "rows": 11, "columns": 1, "legend": ["temperature"]}, "data": [[15.988164344996578], [15.923168208224487], [15.866838042416385], [15.864454833753204], [15.97578711801058], [15.895773634887693], [15.894235919783785], [15.910474543874104], [15.89725421391983], [15.908842296578978], [null]]}
```

To view historical temperature data, navigate to the html directory: `http://raspberrypi:8080/html/temperature`

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
sudo sense-hat-rest.py
```
