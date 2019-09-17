apt-get update


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
                   tango-test

cp .my.cnf /vagrant
mysql mysql -e "insert into server (name,host,mode,level) values ('tangotest/test','buster.localdomain',1,1)" tango

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
                   python3-pytango \
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

pip3 install git+https://github.com/taurus-org/taurus_pyqtgraph.git
pip3 install --no-deps h5py==2.10  # to have VDS


pip3 install --no-deps git+https://github.com/taurus-org/taurus.git@develop
cp ./.bash_profile /vagrant

pip3 install --no-deps git+https://github.com/sardana-org/sardana.git@develop

# Change locale from POSIX to C.UTF-8 due to taurus-org/taurus#836
export LANG=C.UTF-8

# install tools used in the training
apt-get install -y blender \
                   wget

# install KDE desktop
apt-get install -y kde-plasma-desktop
