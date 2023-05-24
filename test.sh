#!/bin/bash
# Sense HAT REST API testing script

HOST="localhost"
PORT="8080"
URL="http://$HOST:$PORT"
CURLRESP="curl -I --write-out '%{http_code}' --silent --output /dev/null"
CURL="curl -sS"

RRDSENSORS=('humidity' 'temperature' 'pressure' 'compass' 'temperature_cpu')
LIVESENSORS=(${RRDSENSORS[@]} 'temperature_from_humidity' 'temperature_from_pressure' 'orientation_radians' 'orientation_degrees'  'orientation' 'compass_raw' 'gyroscope' 'gyroscope_raw' 'accelerometer' 'accelerometer_raw')
PASTSENSORS=(${RRDSENSORS[@]} 'all')
IMAGES=('humidity' 'temperature_c' 'temperature_f' 'pressure' 'compass' 'temperature_cpu')
HTML=(${IMAGES[@]} 'all')
DISPLAY=(${IMAGES[@]})

get() {
    response=$(eval $CURLRESP $1)
    if [ "$response" -ne 200 ] ; then
        echo "Failed ($response): $1"
        exit 1
    fi
    echo "Success (200): $1"
}

getjson() {
     eval $CURL $1 | python -mjson.tool &> /dev/null
     if [ $? -ne 0 ]; then
        echo "Failed (json): $1"
        exit 1
     fi
     echo "Success (json): $1"
}

getimage() {
     if command -v identify &> /dev/null; then
          eval $CURL $1 | identify - &> /dev/null
          if [ $? -ne 0 ]; then
               echo "Failed (image): $1"
               exit 1
          fi
          echo "Success (image): $1"
     else
          get "$1"
     fi
}

# Index
echo "Testing index..."
get "$URL"

# Live sensors
echo "Testing live sensors..."
for sensor in "${LIVESENSORS[@]}"; do
     getjson "$URL/live/$sensor"
done

# Past sensors
echo "Testing past sensors..."
for sensor in "${PASTSENSORS[@]}"; do
     getjson "$URL/past/$sensor"
done

# Images
echo "Testing images..."
for sensor in "${IMAGES[@]}"; do
     getimage "$URL/image/$sensor"
done

# Html
echo "Testing htmls..."
for sensor in "${HTML[@]}"; do
     get "$URL/html/$sensor" 
done

# Display
echo "Testing displays..."
for sensor in "${DISPLAY[@]}"; do
     get "$URL/display/$sensor" 
done

echo "Tests completed successfully!"
