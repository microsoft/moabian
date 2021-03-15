# PROJECT MOAB FIRMWARE

## Build 3.0 (May 2021)

Binary built on Ubuntu 20

## Zephyr dependencies:

```
sudo apt install --no-install-recommends git cmake ninja-build gperf \
    ccache dfu-util device-tree-compiler wget \
    python3-dev python3-pip python3-setuptools python3-tk python3-wheel \
    xz-utils file make gcc gcc-multilib g++-multilib libsdl2-dev
```

## Clone Zephyr 2.1.0

Create a directory called "zephyrproject."

```
cd ~
mkdir zephyrproject
cd zephyrproject
git clone https://github.com/zephyrproject-rtos/zephyr.git
cd zephyr/
git checkout tags/v2.1.0
```

## Install the "West" Zephyr helper toolchain

```
pip3 install --user west imgtool
```

Ensure `.local/bin` is on your PATH:

For BASH:
```
echo 'export PATH=~/.local/bin:"$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Inform West where to find Zephyr v2.1.0

```
cd ..
west init -l zephyr/
west update
```

Install a few Zephyr Python dependencies.

```
pip3 install --user -r zephyr/scripts/requirements.txt
```

Now get the Zephyr SDK (cross-compiler toolchains etc). 

> Install the 0.10.3 Version. 

```
wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.10.3/zephyr-sdk-0.10.3-setup.run
chmod +x zephyr-sdk-0.10.3-setup.run
./zephyr-sdk-0.10.3-setup.run -- -d ~/zephyr-sdk-0.10.3
```


For BASH users, Add a few environment variable settings (also add to your .bashrc):

```
cd ..
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-sdk-0.10.3/
source zephyrproject/zephyr/zephyr-env.sh
```

For ZSH users, add this to the end of your .zshrc

```zsh
cat >> ~/.zshrc <<EOF
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR=$HOME/zephyrproject/sdk/
export ZEPHYR_BASE=$HOME/zephyrproject/zephyr
EOF
```

You've now validated Zephyr and the Hat source build.  The binary is in
`hat/app/build/zephyr/zephyr.bin`

## To build the firmware

For future builds, you can simply run `doit` which does the above, signs
the binary with the MCU bootloader private key, and `scp`s the firmware
directly to moab for flashing.

```
cd src
doit build
doit install
doit clean
```

