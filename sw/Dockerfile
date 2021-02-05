FROM arm32v7/python:3.7-slim-buster
# From https://hub.docker.com/r/arm32v7/python 
# Moabian uses python 3.7 Debian 10 (Buster) "slim", specifically:
# https://github.com/docker-library/python/blob/35d8d9712c3ea4cbc4004a0e62ab61100b6fed99/3.7/buster/slim/Dockerfile

ENV LC_ALL C.UTF-8
ENV DEBIAN_FRONTEND noninteractive
ENV UDEV off

RUN apt-get update && apt-get install -y --no-install-recommends \
	ca-certificates \
	findutils \
	gnupg \
	dirmngr \
	inetutils-ping \
	netbase \
	curl \
	udev \
	procps \
	iproute2 \

	git \
	openssh-client \
	autoconf \
	build-essential \
	libbz2-dev \
	libcurl4-openssl-dev \
	libevent-dev \
	libffi-dev \
	libglib2.0-dev \
	libjpeg-dev \
	libncurses-dev \
	libpq-dev \
	libreadline-dev \
	libssl-dev \
	libxml2-dev \
	libxslt-dev \
	libyaml-dev \
	zlib1g-dev \
  && c_rehash


# 01_nodoc
RUN echo 'path-exclude /usr/share/doc/*\n\
# we need to keep copyright files for legal reasons\n\
path-include /usr/share/doc/*/copyright\n\
path-exclude /usr/share/man/*\n\
path-exclude /usr/share/info/*\n\
path-exclude /usr/share/lintian/*\n\
path-exclude /usr/share/locale/*\n\
path-include /usr/share/locale/en*' > /etc/dpkg/dpkg.cfg.d/01_nodoc


# 01_buildconfig
RUN echo 'APT::Get::Assume-Yes "true";\n\
APT::Install-Recommends "0";\n\
APT::Install-Suggests "0";\n\
quiet "true";' > /etc/apt/apt.conf.d/01_buildconfig

RUN mkdir -p /usr/share/man/man1


RUN echo "deb http://archive.raspbian.org/raspbian buster main contrib rpi" >>  /etc/apt/sources.list \
  && apt-key adv --batch --keyserver ha.pool.sks-keyservers.net  --recv-key 0x9165938D90FDDD2E \
  && echo "deb http://archive.raspberrypi.org/debian buster main ui" >>  /etc/apt/sources.list.d/raspi.list \
  && apt-key adv --batch --keyserver ha.pool.sks-keyservers.net  --recv-key 0x82B129927FA3303E


RUN rm -rf /var/lib/apt/lists/*

RUN find /usr/share/doc -depth -type f ! -name copyright | xargs rm || true \
	&& find /usr/share/doc -empty | xargs rmdir || true \
	&& find /usr/share/locale/* -depth -type d ! -name en* | xargs rm -rf || true \
	&& rm -rf /usr/share/man/* /usr/share/groff/*  /usr/share/info/* \
	&& rm -rf /usr/share/lintian/* /usr/share/linda/* /var/cache/man/*


RUN apt-get update && apt-get install -y --no-install-recommends \
	less \
	kmod \
	nano \
	net-tools \
	ifupdown \
	iputils-ping \
	i2c-tools \
	usbutils \
	wget

##
## Moab specific install
## Must use python3.7
##

WORKDIR /app
COPY bin /app/bin

RUN /app/bin/packages

RUN apt-get -y autoremove && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* 

RUN /app/bin/bcm2835

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt -i https://www.piwheels.org/simple

COPY libs /app/libs
RUN /app/bin/pymoab

RUN apt-get autoremove build-essential cpp-8 gcc-8

COPY control /app/control
COPY main.py /app
CMD python3 main.py -t 5

