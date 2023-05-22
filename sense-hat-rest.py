#!/usr/bin/env python3

import web
import json
import rrdtool
import tempfile
import time
import threading
import os
import subprocess
import configparser
import requests
from datetime import datetime
from sense_hat import SenseHat, ACTION_HELD

sense = SenseHat()

config = configparser.ConfigParser(allow_no_value=True)
config.read("/etc/sense-hat-rest.conf")


# option when joystick held down
MIDHELD = config.get('sense-hat', 'MIDHELD')


def pushed_middle(event):
    if event.action == ACTION_HELD and MIDHELD:
        if MIDHELD == 'reboot' or MIDHELD == 'poweroff':
            sense.clear(255, 0, 0)
            time.sleep(1)
            sense.clear()
            time.sleep(1)
            subprocess.run(MIDHELD, shell=True)


sense.stick.direction_middle = pushed_middle

# get sensor data
TEMPCALIB = config.getfloat('sense-hat', 'TEMPCALIB')


def get_sensor(sensor):
    data = {}

    if sensor == 'humidity':
        data[sensor] = sense.humidity
    elif sensor == 'temperature':
        data[sensor] = sense.temperature + TEMPCALIB
    elif sensor == 'temperature_from_humidity':
        data[sensor] = sense.get_temperature_from_humidity()
    elif sensor == 'temperature_from_pressure':
        data[sensor] = sense.get_temperature_from_pressure()
    elif sensor == 'pressure':
        data[sensor] = sense.pressure
    elif sensor == 'orientation_radians':
        data[sensor] = sense.orientation_radians
    elif sensor == 'orientation_degrees':
        data[sensor] = sense.get_orientation_degrees()
    elif sensor == 'orientation':
        data[sensor] = sense.orientation
    elif sensor == 'compass':
        data[sensor] = sense.compass
    elif sensor == 'compass_raw':
        data[sensor] = sense.compass_raw
    elif sensor == 'gyroscope':
        data[sensor] = sense.gyroscope
    elif sensor == 'gyroscope_raw':
        data[sensor] = sense.gyroscope_raw
    elif sensor == 'accelerometer':
        data[sensor] = sense.accelerometer
    elif sensor == 'accelerometer_raw':
        data[sensor] = sense.accelerometer_raw
    elif sensor == 'temperature_cpu':
        data[sensor] = float(subprocess.check_output(
            "cat /sys/class/thermal/thermal_zone0/temp", shell=True))/1000

    sense.set_imu_config(True, True, True)

    return data


# rrdtool data gather thread
RRDSENSORS = ['humidity', 'temperature',
              'pressure', 'compass', 'temperature_cpu']


def rrdthread(database, step):
    while True:
        template = ''
        data = 'N:'
        for i in RRDSENSORS:
            sensor = get_sensor(i)
            data += '%s:' % sensor[i]
            template += '%s:' % i
        data = data[:-1]  # remove last ':'
        template = template[:-1]
        args = ['--template']
        args += [template, data]
        rrdtool.update(database, args)
        time.sleep(step)


# ifttt notification
IFTTTKEY = config.get('notify', 'IFTTTKEY')
IFTTTEVENT = config.get('notify', 'IFTTTEVENT')


def ifttt_send(value1, value2, value3):
    url = 'https://maker.ifttt.com/trigger/' + IFTTTEVENT + '/with/key/' + IFTTTKEY
    headers = {'Accept': 'application/json',
               'Content-type': 'application/json'}
    payload = {'value1': value1, 'value2': value2, 'value3': value3}
    r = requests.post(url, headers=headers, json=payload)
    return r.text

# celsius to fahrenheit


def celsiustofahr(celsius):
    fahr = (celsius * 9/5) + 32
    return fahr

# get current fahrenheit temperature


def getfahr():
    json = get_sensor('temperature')
    temperature = json["temperature"]
    return celsiustofahr(temperature)

# temperature to string


def strtemp(temp):
    return "%.1f" % temp


# notification thread
NOTIFYSTEP = config.getint('notify', 'NOTIFYSTEP')
MINTEMP = config.getfloat('notify', 'MINTEMP')
MAXTEMP = config.getfloat('notify', 'MAXTEMP')


def notifythread():
    while True:
        temp = getfahr()
        if temp < MINTEMP:
            message = 'WARNING: current temp ' + \
                strtemp(temp) + ' is below min ' + strtemp(MINTEMP)
            print(message)
            if IFTTTKEY and IFTTTEVENT:
                response = ifttt_send(message, None, None)
                print(response)
        if temp > MAXTEMP:
            message = 'WARNING: current temp ' + \
                strtemp(temp) + ' is above max ' + strtemp(MAXTEMP)
            print(message)
            if IFTTTKEY and IFTTTEVENT:
                response = ifttt_send(message, None, None)
                print(response)
        time.sleep(NOTIFYSTEP)


# start notfication thread
if NOTIFYSTEP > 0:
    thread = threading.Thread(target=notifythread)
    thread.start()


# initialize database
# number of seconds between each data point
DBSTEP = config.getint('rrd', 'DBSTEP')
DBFILE = config.get('rrd', 'DBFILE')  # database file path
DBDAYS = config.getint('rrd', 'DBDAYS')  # number of days to retain data
if not (os.path.exists(DBFILE)):
    args = ["--start", "N", "--step", "%s" % DBSTEP, "DS:humidity:GAUGE:%s:0:100" % (DBSTEP*2), "DS:temperature:GAUGE:%s:-100:100" % (DBSTEP*2), "DS:temperature_cpu:GAUGE:%s:-100:100" % (
        DBSTEP*2), "DS:pressure:GAUGE:%s:850:1100" % (DBSTEP*2), "DS:compass:GAUGE:%s:0:360" % (DBSTEP*2), "RRA:MAX:0.5:1:%s" % (int(60/DBSTEP*60*24*DBDAYS))]
    print('Creating database' + DBFILE + ' with args ', args)
    rrdtool.create(DBFILE, args)

# start sensor data gather thread
thread = threading.Thread(target=rrdthread, args=[DBFILE, DBSTEP])
thread.start()

LIVESENSORS = RRDSENSORS + ['temperature_from_humidity', 'temperature_from_pressure', 'orientation_radians',
                            'orientation_degrees', 'orientation', 'compass_raw', 'gyroscope', 'gyroscope_raw', 'accelerometer', 'accelerometer_raw']
PASTSENSORS = RRDSENSORS + ['all']
IMAGES = ['humidity', 'temperature_c', 'temperature_f',
          'pressure', 'compass', 'temperature_cpu']
HTML = IMAGES + ['all']
DISPLAY = IMAGES

# web api
urls = (
    '/live/(.*)', 'get_live',
    '/past/(.*)', 'get_past',
    '/image/(.*)', 'get_image',
    '/html/(.*)', 'get_html',
    '/display/(.*)', 'get_display',
    '/', 'get_index'
)

app = web.application(urls, globals())

# returns json of live sensor data


class get_live:
    def GET(self, action):
        data = {}

        if action in LIVESENSORS:
            data = get_sensor(action)
        else:
            raise web.notfound()

        web.header('Content-Type', 'application/json')

        return json.dumps(data)

# returns json of past sensor data


class get_past:
    def GET(self, action):
        input = web.input(start='1h')  # defaults
        start = str(input.start)
        sensor = str(action)
        args = ["--start", "-%s" % start, "--json"]
        if action in RRDSENSORS:
            elements = ["DEF:%s=%s:%s:MAX" %
                        (sensor, DBFILE, sensor), "XPORT:%s:%s" % (sensor, sensor)]
        elif action == 'all':
            elements = []
            for i in RRDSENSORS:
                elements += ["DEF:%s=%s:%s:MAX" %
                             (i, DBFILE, i), "XPORT:%s:%s" % (i, i)]
        else:
            raise web.notfound()

        data = rrdtool.xport(elements, args)

        web.header('Content-Type', 'application/json')

        return json.dumps(data)

# returns a image of sensor over time


class get_image:
    def GET(self, action):

        WATERMARK = 'Sense HAT Raspberry Pi'

        HUMIDDEF = 'DEF:humidity=%s:humidity:MAX' % DBFILE
        HUMIDDATEVDEF = 'VDEF:date=humidity,LAST'
        HUMIDLINE = 'LINE2:humidity#0000FF:humidity'
        HUMIDGPRINT = 'GPRINT:humidity:LAST:Current\: %.1lf%%'

        TEMPDEF = 'DEF:temperature=%s:temperature:MAX' % DBFILE
        TEMPDATEVDEF = 'VDEF:date=temperature,LAST'
        TEMPFAHRCDEF = 'CDEF:tempfahr=9,5,/,temperature,*,32,+'  # conversion of C to F
        TEMPFAHRLINE = 'LINE2:tempfahr#FFA500:fahrenheit'
        TEMPFAHRGPRINT = 'GPRINT:tempfahr:LAST:Current\: %.1lf\u2109'
        TEMPCELCLINE = 'LINE2:temperature#FF0000:celsius'
        TEMPCELCGPRINT = 'GPRINT:temperature:LAST:Current\: %.1lf\u2103'

        CPUTEMPDEF = 'DEF:temperature_cpu=%s:temperature_cpu:MAX' % DBFILE
        CPUFAHRCDEF = 'CDEF:cpufahr=9,5,/,temperature_cpu,*,32,+'  # conversion of C to F
        CPUDATEVDEF = 'VDEF:date=temperature_cpu,LAST'
        CPUCELCLINE = 'LINE2:temperature_cpu#FF0000:celsius'
        CPUCELCGPRINT = 'GPRINT:temperature_cpu:LAST:Current\: %.1lf\u2103'

        PRESDEF = 'DEF:pressure=%s:pressure:MAX' % DBFILE
        PRESDATEVDEF = 'VDEF:date=pressure,LAST'
        PRESLINE = 'LINE2:pressure#00FF00:pressure'
        PRESGPRINT = 'GPRINT:pressure:LAST:Current\: %.1lfmb'

        COMPDEF = 'DEF:compass=%s:compass:MAX' % DBFILE
        COMPDATEVDEF = 'VDEF:date=compass,LAST'
        COMPLINE = 'LINE2:compass#FFFF00:north'
        COMPGPRINT = 'GPRINT:compass:LAST:Current\: %.1lfN'

        DATEGPRINT = 'GPRINT:date:%F %R:strftime'

        input = web.input(start='1h', width=600, height=400)  # defaults
        start = str(input.start)
        width = str(input.width)
        height = str(input.height)
        sensor = str(action)

        args = ["--start", "-%s" % start, "--width", "%s" % width, "--height", "%s" %
                height, "--watermark", "%s" % WATERMARK]
        if action == 'humidity':
            args += ["--title", "Humidity", "--vertical-label", "percent", "%s" % HUMIDDEF,
                     "%s" % HUMIDDATEVDEF, "%s" % HUMIDLINE, "%s" % HUMIDGPRINT]
        elif action == 'temperature_c':
            args += ["--title", "Temperature", "--vertical-label", "degrees", "%s" %
                     TEMPDEF,  "%s" % TEMPDATEVDEF, "%s" % TEMPCELCLINE, "%s" % TEMPCELCGPRINT]
        elif action == 'temperature_f':
            args += ["--title", "Temperature", "--vertical-label", "degrees", "%s" % TEMPDEF, "%s" %
                     TEMPFAHRCDEF, "%s" % TEMPDATEVDEF, "%s" % TEMPFAHRLINE, "%s" % TEMPFAHRGPRINT]
        elif action == 'temperature_cpu':
            args += ["--title", "CPU Temperature", "--vertical-label", "degrees", "%s" % CPUTEMPDEF, "%s" %
                     CPUFAHRCDEF, "%s" % CPUDATEVDEF, "%s" % CPUCELCLINE, "%s" % CPUCELCGPRINT]
        elif action == 'pressure':
            args += ["--title", "Pressure", "--vertical-label", "millibars", "--upper-limit", "1100", "--lower-limit",
                     "850", "%s" % PRESDEF, "%s" % PRESDATEVDEF, "%s" % PRESLINE, "%s" % PRESGPRINT]
        elif action == 'compass':
            args += ["--title", "Compass", "--vertical-label", "degrees", "%s" % COMPDEF,
                     "%s" % COMPDATEVDEF, "%s" % COMPLINE, "%s" % COMPGPRINT]
        else:
            raise web.notfound()

        args += ["%s" % DATEGPRINT]

        fp = tempfile.NamedTemporaryFile()
        fname = str(fp.name)

        rrdtool.graph(fname, args)

        web.header("Content-Type", "image/png")

        return open(fname, "rb").read()

# returns html of images


class get_html:
    def GET(self, action):
        input = web.input(start='1d', width=600, height=400)  # defaults
        start = str(input.start)
        width = str(input.width)
        height = str(input.height)
        sensor = str(action)
        query = '?start=%s&width=%s&height=%s' % (start, width, height)

        data = '<html><head><meta http-equiv="refresh" content="%s"><title>%s</title></head>' % (
            DBSTEP, sensor)
        if action in IMAGES:
            image = '/image/%s%s' % (sensor, query)
            data += '<a href="%s" target="_blank"><img src="%s"/></a>' % (
                image, image)
        elif action == 'all':
            for i in IMAGES:
                image = '/image/%s%s' % (i, query)
                data += '<a href="%s"target="_blank"><img src="%s"/></a>' % (
                    image, image)
        else:
            raise web.notfound()
        data += '</html>'

        web.header("Content-Type", "text/html")

        return data

# returns string of live sensor data


class get_display:
    def GET(self, action):
        data = {}
        value = "0"

        if action in DISPLAY:
            data = get_sensor(action)
            if action == 'humidity':
                value = "%.1f%%" % data["humidity"]
                sense.show_message(value, text_colour=[0, 0, 255])
            elif action == 'temperature_c':
                data = get_sensor('temperature')
                value = "%.1fC" % data["temperature"]
                sense.show_message(value, text_colour=[255, 0, 0])
            elif action == 'temperature_f':
                data = get_sensor('temperature')
                value = "%.1fF" % celsiustofahr(data["temperature"])
                sense.show_message(value, text_colour=[255, 165, 0])
            elif action == 'pressure':
                value = "%.1fmb" % data["pressure"]
                sense.show_message(value, text_colour=[0, 255, 0])
            elif action == 'compass':
                value = "%.1fN" % data["compass"]
                sense.show_message(value, text_colour=[255, 255, 0])
            elif action == 'temperature_cpu':
                value = "%.1fC" % data["temperature_cpu"]
                sense.show_message(value, text_colour=[255, 0, 0])

        else:
            raise web.notfound()

        web.header('Content-Type', 'application/json')

        return value

# returns usage page


class get_index:
    def GET(self):
        host = 'http://' + web.ctx.host
        TITLE = 'Sense HAT REST API'
        PARAMS = '[?start=n[days|hours|minutes|seconds]]'
        IMAGEPARAMS = PARAMS + '[&width=n][&height=n]'
        year = datetime.now().strftime("%Y")

        data = '<html><head><title>%s</title></head>' % TITLE
        data += '<h1>%s</h1>' % TITLE
        data += '<h2>Live sensor json</h2>'
        url = '%s/live/' % host
        data += '<p>%s[' % url
        for i in LIVESENSORS:
            data += '<a href="%s%s" target="_blank">%s</a>|' % (url, i, i)
        data = data[:-1]  # remove last '|'
        data += ']</p>'

        data += '<br><h2>Past sensor json</h2>'
        url = '%s/past/' % host
        data += '<p>%s[' % url
        for i in PASTSENSORS:
            data += '<a href="%s%s" target="_blank">%s</a>|' % (url, i, i)
        data = data[:-1]  # remove last '|'
        data += ']%s</p>' % PARAMS

        data += '<br><h2>Past sensor images</h2>'
        url = '%s/image/' % host
        data += '<p>%s[' % url
        for i in IMAGES:
            data += '<a href="%s%s" target="_blank">%s</a>|' % (url, i, i)
        data = data[:-1]  # remove last '|'
        data += ']%s</p>' % IMAGEPARAMS

        data += '<br><h2>Past sensor html</h2>'
        url = '%s/html/' % host
        data += '<p>%s[' % url
        for i in HTML:
            data += '<a href="%s%s" target="_blank">%s</a>|' % (url, i, i)
        data = data[:-1]  # remove last '|'
        data += ']%s</p>' % IMAGEPARAMS

        data += '<br><h2>Display sensor on LED</h2>'
        url = '%s/display/' % host
        data += '<p>%s[' % url
        for i in DISPLAY:
            data += '<a href="%s%s" target="_blank">%s</a>|' % (url, i, i)
        data = data[:-1]  # remove last '|'
        data += ']</p>'

        data += '<br><footer>'
        data += 'Copyright %s <a href="https://github.com/jithware/sense-hat-rest" target="_blank">Jithware</a>' % year
        data += '</footer>'
        data += '</html>'

        web.header("Content-Type", "text/html")

        return data


# start the web server
if __name__ == "__main__":
    app.run()
