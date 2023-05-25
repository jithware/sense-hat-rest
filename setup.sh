#! /bin/sh

# install required packages
sudo apt-get -y install python3-sense-hat rrdtool python3-rrdtool python3-webpy python3-requests 

# copy over the files
[ ! -f "/etc/sense-hat-rest.conf" ] && sudo install -v ./sense-hat-rest.conf /etc || echo "keeping existing '/etc/sense-hat-rest.conf' you may need to add new configurations"
sudo install -v -d /usr/share/sense-hat-rest/static/ # create directories
sudo install -v -m 755 ./sense-hat-rest.py /usr/share/sense-hat-rest/ # rest api python script
sudo install -v ./static/* /usr/share/sense-hat-rest/static/ # static files
sudo install -v ./sense-hat-rest.service /lib/systemd/system/ # systemd service
sudo install -v -d /var/cache/sense-hat # database path

# enable service
sudo systemctl enable sense-hat-rest.service

# restart the daemon
sudo systemctl restart sense-hat-rest.service

# status of the daemon
sudo systemctl --no-pager status sense-hat-rest.service

echo ""
echo "For usage see: http://localhost:8080/"
echo ""
