FROM debian:buster

# change installation dialogs policy to noninteractive
# otherwise debconf raises errors: unable to initialize frontend: Dialog
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get install -y blender python3-pip git python3-h5py python3-numpy python3-pillow python3-gevent

RUN pip3 install "git+https://github.com/sardana-org/sardana-training/#egg=blender-slits&subdirectory=blender-slits"

EXPOSE 9999/tcp

CMD blender-slits-server