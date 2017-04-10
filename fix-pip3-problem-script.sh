sudo -i
apt-get purge -y python3-pip
wget https://bootstrap.pypa.io/get-pip.py28
python3 ./get-pip.py
apt-get install python3-pip
