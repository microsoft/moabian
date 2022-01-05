import subprocess
import json
import sys
from dataclasses import dataclass


@dataclass
class BonsaiImage:
    image: str  # image	scotstanws.azurecr.io/00000000-0000-0000-0000-000000000000/circle:2-linux-arm32v7
    brain_id: str  # 'circle'
    version: str  # 2 or empty ''
    short_name: str  # 'circle:2'  (maximum of 9 chars if no version else truncated to 6 chars)
    port: int  # port number
    iotedge: bool  # true if this brain is managed by IOT Edge


def ps():
    docker_ps = subprocess.Popen(
        "docker ps --format '{{json .}}'",
        stdout=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout = docker_ps.communicate()[0]

    if docker_ps.returncode == 0:
        docker_images = json.loads(reformat_json(stdout))
        bonsai_images = list_to_bonsai_images(docker_images)
        return bonsai_images


def reformat_json(stdout):
    # docker ps returns invalid json
    # split the json objects on the newline

    json = "["
    lines = stdout.splitlines()
    for i, line in enumerate(lines):
        json += line
        # add comma between each json object
        if i != len(lines) - 1:
            json += ","

    # Add ending bracket for well-formed json
    json += "]"
    return json


def get_port(splitports):
    # port format: 'Ports': '0.0.0.0:5005->5000/tcp, :::5005->5000/tcp'
    print(splitports)
    if splitports is not None:
        # split on comma first - 0.0.0.0:5005->5000/tcp
        splitport_1 = splitports.split(",")[0]
        # split next on arrow - 0.0.0.0:5005
        splitport_2 = splitport_1.split("->")[0]
        # finally split on colon and take last element - 5005
        port = splitport_2.split(":")[1]
    else:
        port = 0

    return port


def get_image_info(image_name, networks, port):
    # split image on slashes
    version = 0
    slashes = image_name.split("/")
    if slashes is not None:

        # if image tag or no slashes, use the image name
        if len(slashes) == 1:
            brain_id = image_name
            short_name = brain_id[:9]

        else:
            # if there's a colon in the name, use it for version
            colon = slashes[-1].split(":")

            if colon and len(colon) > 1:
                version_split = colon[1].split("-")
                # if version_split, account for dashes
                if version_split is not None:
                    version = version_split[0]
                    brain_id = colon[0]
                    short_name = brain_id[:6] + ":" + version
                else:
                    brain_id = colon[0]
                    short_name = brain_id[:9]
            else:
                # brain_id will be the last split on slashes
                brain_id = slashes[-1]
                short_name = brain_id[:9]

    bonsai_image = BonsaiImage(
        image=image_name,
        brain_id=brain_id,
        version=version,
        short_name=short_name,
        port=int(port),
        iotedge=networks=="azure-iot-edge"
    )
    return bonsai_image


def list_to_bonsai_images(iot_dict):
    # list of BonsaiImages to return
    bonsai_images = []

    # parse the iot_dict list
    for x, info in enumerate(iot_dict):

        if (info["Names"] != "edgeHub") and (info["Names"] != "edgeAgent"):
            # check for port
            if "Ports" in info.keys():
                port = get_port(info["Ports"])
                bonsai_image = get_image_info(info["Image"], info["Networks"], port)
                bonsai_images.append(bonsai_image)

    return bonsai_images


if __name__ == "__main__":
    print(ps())
