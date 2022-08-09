# FROM [--platform=amd64] debian:buster-slim
FROM debian:buster-slim

RUN apt-get update -y && apt-get upgrade -y

RUN apt install --no-install-recommends -y git cmake \
    build-essential curl ninja-build gperf \
    ccache dfu-util device-tree-compiler wget \
    python3-dev python3-pip python3-setuptools python3-tk python3-wheel \
    xz-utils file make gcc gcc-multilib g++-multilib libsdl2-dev

# TODO: Change app to src
WORKDIR /app

ENV ZEPHYR_TOOLCHAIN_VARIANT=zephyr
ENV ZEPHYR_SDK_INSTALL_DIR=/app/zephyrproject/zephyr-sdk-0.10.3/

RUN mkdir /app/zephyrproject \
    && mkdir /app/zephyrproject/zephyr \
    && git clone --depth 1 --branch v2.1.0 https://github.com/zephyrproject-rtos/zephyr.git /app/zephyrproject/zephyr

RUN python3 -m pip install --upgrade pip \
    && pip3 install west imgtool

WORKDIR /app/zephyrproject

RUN west init -l /app/zephyrproject/zephyr
RUN west update

RUN pip3 install -r /app/zephyrproject/zephyr/scripts/requirements.txt

RUN wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.10.3/zephyr-sdk-0.10.3-setup.run -P /app/zephyrproject/ \
    && chmod +x /app/zephyrproject/zephyr-sdk-0.10.3-setup.run \
    && /app/zephyrproject/zephyr-sdk-0.10.3-setup.run -- -d /app/zephyrproject/zephyr-sdk-0.10.3

# TODO: Move this up to the top
ENV ZEPHYR_BASE=/app/zephyrproject/zephyr

SHELL ["/bin/bash", "-c"]
RUN source /app/zephyrproject/zephyr/zephyr-env.sh

# TODO: Change app to src
WORKDIR /app
COPY . /app

CMD ["bash", "-c", "./doit", "docker"]