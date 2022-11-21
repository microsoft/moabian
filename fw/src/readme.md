```sh
docker build --platform linux/amd64 -t firmware .
docker run -e VERSION=3.3 --rm -it -v "$(pwd)"/output:/app/output firmware
cp output/v3.3.xxxxx.bin ../v3.3.bin
```
