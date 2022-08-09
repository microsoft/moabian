FROM --platform=amd64 debian:buster-slim AS zephyr
# FROM debian:buster-slim

RUN apt-get update -y && apt-get upgrade -y

RUN apt install --no-install-recommends -y git cmake \
    build-essential curl ninja-build gperf \
    ccache dfu-util device-tree-compiler wget \
    python3-dev python3-pip python3-setuptools python3-tk python3-wheel \
    xz-utils file make gcc gcc-multilib g++-multilib libsdl2-dev

# TODO: Change app to src
WORKDIR /root

ENV ZEPHYR_TOOLCHAIN_VARIANT=zephyr
ENV ZEPHYR_SDK_INSTALL_DIR=/root/zephyrproject/zephyr-sdk-0.10.3/
ENV ZEPHYR_BASE=/root/zephyrproject/zephyr

RUN mkdir /root/zephyrproject \
    && mkdir /root/zephyrproject/zephyr \
    && git clone --depth 1 --branch v2.1.0 https://github.com/zephyrproject-rtos/zephyr.git /root/zephyrproject/zephyr

RUN python3 -m pip install --upgrade pip \
    && pip3 install west imgtool

WORKDIR /root/zephyrproject

RUN west init -l /root/zephyrproject/zephyr
RUN west update

RUN pip3 install -r /root/zephyrproject/zephyr/scripts/requirements.txt

RUN wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.10.3/zephyr-sdk-0.10.3-setup.run -P /root/zephyrproject/ \
    && chmod +x /root/zephyrproject/zephyr-sdk-0.10.3-setup.run \
    && /root/zephyrproject/zephyr-sdk-0.10.3-setup.run -- -d /root/zephyrproject/zephyr-sdk-0.10.3

SHELL ["/bin/bash", "-c"]
RUN source /root/zephyrproject/zephyr/zephyr-env.sh

# TODO: Change app to src
WORKDIR /root
COPY . /root

CMD ["./doit", "build"]