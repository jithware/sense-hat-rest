#! /bin/sh

# install required packages
sudo apt-get -y install python3-sense-hat rrdtool python3-rrdtool python3-requests python3-pip

# install required python modules
sudo pip3 install web.py

# copy over the files
sudo install -v ./sense-hat-rest.conf /etc # configuration file
sudo install -v ./sense-hat-rest.py /usr/bin/ # rest api script
sudo install -v ./sense-hat-rest.service /lib/systemd/system/ # rest api service
sudo install -v -d /var/cache/sense-hat # database path

# enable service
sudo systemctl enable sense-hat-rest.service

# restart the daemon
sudo systemctl restart sense-hat-rest.service

echo ""
echo "For usage see: http://localhost:8080/"
echo ""
