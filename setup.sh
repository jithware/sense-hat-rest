#! /bin/sh

# install required packages
apt-get -y install python-sense-hat python3-sense-hat rrdtool python-rrdtool

# install required python modules
easy_install web.py

# copy over the files
install -v ./sense-hat-rest /etc/init.d/ # rest api service
install -v ./sense-hat-rest.py /usr/bin/ # rest api script

# enable service
update-rc.d sense-hat-rest defaults

# restart the daemon
service sense-hat-rest restart

echo ""
echo "For usage see: http://localhost/"
echo ""
