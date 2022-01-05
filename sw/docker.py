# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import json
import argparse
import requests
import subprocess

from dataclasses import dataclass


@dataclass
class BonsaiImage:
    image: str  # scotstanws.azurecr.io/00000000-0000-0000-0000-000000000000/circle:2-linux-arm32v7
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
        bonsai_images = sorted(bonsai_images, key=lambda x: x.port)
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


def get_resp(port, client_id=123):
    # Test that port has a valid brain
    resp_status = requests.get(f"http://localhost:{port}/v1/status").status_code
    valid_brain = resp_status == 200

    if not valid_brain:
        raise ValueError(f"Port {port} is not a valid Bonsai brain")

    # Test whether the brain is v1 or v2 (also resets memory if a v2 brain)
    resp_delete = requests.delete(
        f"http://localhost:{port}/v2/clients/{client_id}"
    ).status_code
    version = 2 if resp_delete == 204 else 1

    if version == 1:
        prediction_url = f"http://localhost:{port}/v1/prediction"
    elif version == 2:
        prediction_url = f"http://localhost:{port}/v2/clients/{client_id}/predict"
    else:
        raise ValueError("Brain version `{version}` is not supported.")

    return version, resp_status, resp_delete


def get_api_url(port, version):
    process = subprocess.Popen(
        "ip route get 1.1.1.1 | head -1 | cut -d' ' -f7",
        stdout=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )
    ip, stderr = process.communicate()
    ip = ip.strip()  # remove newline

    if version == 1:
        api_url = f"http://{ip}:{port}/v1/doc/index.html"
    elif version == 2:
        api_url = f"http://{ip}:{port}/swagger.html"
    else:
        raise ValueError("Brain version `{version}` is not supported.")
    return api_url


def get_image_info(info, port):
    image_name = info["Image"]
    container_name = info["Names"]

    # Use image name if there are no container names
    if container_name is None:
        container_name = image_name

    # split image on slashes
    version = 0
    slashes = image_name.split("/")

    # if image tag or no slashes, use the image name
    if slashes is not None:
        if len(slashes) == 1:
            brain_id = image_name
            short_name = container_name[:9]

        else:
            # if there's a colon in the name, use it for version
            colon = slashes[-1].split(":")

            if colon and len(colon) > 1:
                version_split = colon[1].split("-")
                # if version_split, account for dashes
                if version_split is not None:
                    version = version_split[0]
                    brain_id = colon[0]
                    short_name = container_name[:6] + ":" + version
                else:
                    brain_id = colon[0]
                    short_name = container_name[:9]
            else:
                # brain_id will be the last split on slashes
                brain_id = slashes[-1]
                short_name = container_name[:9]

    bonsai_image = BonsaiImage(
        image=image_name,
        brain_id=brain_id,
        version=version,
        short_name=short_name,
        port=int(port),
        iotedge=info["Networks"] == "azure-iot-edge",
    )
    return bonsai_image


def list_to_bonsai_images(iot_dict):
    # list of BonsaiImages to return
    bonsai_images = []

    # parse the iot_dict list
    for info in iot_dict:
        if (info["Names"] != "edgeHub") and (info["Names"] != "edgeAgent"):
            # check for port
            if "Ports" in info.keys():
                port = get_port(info["Ports"])
                bonsai_image = get_image_info(info, port)
                bonsai_images.append(bonsai_image)

    return bonsai_images


if __name__ == "__main__":
    print(ps())
