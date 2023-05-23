#!/bin/bash
# Sense HAT REST API testing script

HOST="localhost"
PORT="8080"
URL="http://$HOST:$PORT"
CURL="curl --write-out '%{http_code}' --silent --output /dev/null"

RRDSENSORS=('humidity' 'temperature' 'pressure' 'compass' 'temperature_cpu')
LIVESENSORS=(${RRDSENSORS[@]} 'temperature_from_humidity' 'temperature_from_pressure' 'orientation_radians' 'orientation_degrees'  'orientation' 'compass_raw' 'gyroscope' 'gyroscope_raw' 'accelerometer' 'accelerometer_raw')
PASTSENSORS=(${RRDSENSORS[@]} 'all')
IMAGES=('humidity' 'temperature_c' 'temperature_f' 'pressure' 'compass' 'temperature_cpu')
HTML=(${IMAGES[@]} 'all')
DISPLAY=(${IMAGES[@]})

get() {
    response=$(eval $CURL $1)
    if [[ "$response" -ne 200 ]] ; then
        echo "Failed ($response): $1"
        exit 1
    fi
    echo "Success (200): $1"
}

# Live sensors
for sensor in "${LIVESENSORS[@]}"; do
     get "$URL/live/$sensor" 
done

# Past sensors
for sensor in "${PASTSENSORS[@]}"; do
     get "$URL/past/$sensor" 
done

# Images
for sensor in "${IMAGES[@]}"; do
     get "$URL/image/$sensor" 
done

# Html
for sensor in "${HTML[@]}"; do
     get "$URL/html/$sensor" 
done

# Display
for sensor in "${DISPLAY[@]}"; do
     get "$URL/display/$sensor" 
done
