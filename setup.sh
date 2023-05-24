#! /bin/sh

# install required packages
sudo apt-get -y install python3-sense-hat rrdtool python3-rrdtool python3-webpy python3-requests 

# copy over the files
[ ! -f "/etc/sense-hat-rest.conf" ] && sudo install -v ./sense-hat-rest.conf /etc || echo "keeping existing '/etc/sense-hat-rest.conf' you may need to add new configurations"
sudo install -v ./sense-hat-rest.py /usr/bin/ # rest api script
sudo install -v ./sense-hat-rest.service /lib/systemd/system/ # rest api service
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
