#! /bin/sh

# install required packages
apt-get -y install python-sense-hat python3-sense-hat rrdtool python-rrdtool

# install required python modules
easy_install web.py

# copy over the files
install -v ./sense-hat-rest.conf /etc # configuration file
install -v ./sense-hat-rest.py /usr/bin/ # rest api script
install -v ./sense-hat-rest.service /lib/systemd/system/ # rest api service
install -v -d /var/cache/sense-hat # database path

# enable service
systemctl enable sense-hat-rest.service

# restart the daemon
systemctl restart sense-hat-rest.service

echo ""
echo "For usage see: http://localhost/"
echo ""
