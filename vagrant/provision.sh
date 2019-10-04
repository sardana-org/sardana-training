gpt-get update


# change installation dialogs policy to noninteractive
# otherwise debconf raises errors: unable to initialize frontend: Dialog
export DEBIAN_FRONTEND=noninteractive

# install some utilities
apt-get install -y python3-pip \
                   git \
                   procps \
                   vim

# install mysql server
apt-get install -y default-mysql-server

#install tango-db
apt-get install -y tango-db \
                   tango-test \
                   python3-tango
#python3 -c "from tango import Database, DbServerInfo; \
#            serv_info = DbServerInfo(); \
#            serv_info.name = 'tangotest/test'; \
#            serv_info.host = 'buster.localdomain'; \
#            serv_info.mode = 1; \
#            serv_info.level = 1; \
#            Database().put_server_info(serv_info);"
#python3 -c "from tango import DeviceProxy; \
#            starter = DeviceProxy('tango/admin/buster'); \
#            starter.DevStartAll(1);"

# install taurus dependencies
apt-get install -y python3-numpy \
                   python3-pyqt5 \
                   python3-pyqt5.qtopengl \
                   python3-pyqt5.qtwebkit \
                   python3-h5py \
                   python3-lxml \
                   python3-pint \
                   python3-future \
                   python3-ply \
                   python3-spyderlib \
                   python3-pymca5 \
                   qttools5-dev-tools \
                   python3-sphinx-rtd-theme \
                   graphviz \
                   python3-pyqtgraph \
                   python3-guiqwt \
                   python3-click

# install sardana dependencies
apt-get install -y python3-qtconsole \
                   python3-itango \
                   python3-matplotlib \
                   ipython3  # to have launcher of ipython

pip3 install --no-deps git+https://github.com/taurus-org/taurus_pyqtgraph.git
pip3 install --no-deps h5py==2.10  # to have VDS


# For taurus 
echo "export QT_API=pyqt5" >> /home/vagrant/.bashrc

# Change locale from POSIX to C.UTF-8 due to taurus-org/taurus#836
export LANG=C.UTF-8

# install tools used in the training
apt-get install -y blender \
                   wget \
                   emacs \
                   vim \
                   okular

# install gevent for blender-slits
apt-get install python3-gevent

# install virtualevn for installation of silx
apt-get install -y virtualenv

# configure PATH to point to pip user installation dir 
echo "export PATH=/home/vagrant/.local/bin:$PATH" >> /home/vagrant/.bashrc

# install KDE desktop
apt-get install -y kde-plasma-desktop

# don't eliminate /tmp directory (by default environment is stored there)
echo "d /tmp 1777 root root -" > /etc/tmpfiles.d/tmp.conf

# clone training materials
git clone https://github.com/sardana-org/sardana-training.git /home/vagrant/sardana-training
# Manual steps:
# 1. Install silx due to a bug in buster package on KDE env:
#
# mkdir ~/.local/bin
# vi ~/.local/bin/silx (#!/usr/bin/bash; source /home/vagrant/silx-venv/bin/activate; silx "$@";)
# chmod 755 .local/bin/silx
# virtualenv -p /usr/bin/python3 silx-venv
# source silx-venv/bin/activate
# pip3 install python-dateutil matplotlib PyQt5 silx
#
# 2. Disable screen lock (may hang VM)
