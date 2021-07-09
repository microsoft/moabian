import subprocess
import json
import sys
from dataclasses import dataclass

# Image name Test cases 

#    = image name more than 1 slash 

#       = 1 colon, more than 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-linux-arm32v7
#       = 1 colon, no dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2
#       = 1 colon, 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-arm32v7

#       = more than 1 colon, no dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:er
#       = more than 1 colon, 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32v7
#       = more than 1 colon, more than 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32-v7

#       = no colon, no dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle
#       = no colon 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux
#       = no colon more than 1 dash  - scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux-arm32v7

#    = image name 1 slash 

#       = no colon, no dash - moab/brain
#       = no colon, 1 dash - moab/brain:3:3-linux
#       = no colon, more than 1 dash - moab/brain:3:3-linux-v32

#       = 1 colon, no dash - moab/brain:3
#       = 1 colon, 1 dash - moab/brain:3-linux
#       = 1 colon more than 1 dash - moab/brain:3-linux-v32

#       = more than 1 colon, no dash - moab/brain:3:3
#       = more than 1 colon, 1 dash - moab/brain:3:3-linux
#       = more than 1 colon, more than 1 dash - moab/brain:3:3-linux-v32

#     = image name no slash 

#       = no colon no dash - den1
#       = no colon 1 dash - 3-linux
#       = no colon more than 1 dash - v2-02-rg

#       = 1 colon no dash - den1:v2
#       = 1 colon 1 dash - den1:3-linux
#       = 1 colon more than 1 dash - den1:v2-02-rg

#       = more than 1 colon no dash - den1:v2:hi
#       = more than 1 colon more than 1 dash - den1:v2:-02-rg
#       = more than 1 colon no dash - den1:v2:23

@dataclass
class BonsaiImage:
    image: str  # image     scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-linux-arm32v7
    brain_id: str  # 'circle'
    version: str  # 2 or empty ''
    short_name: str  # 'circle:2'  (maximum of 9 chars if no version else truncated to 6 chars)
    port: int  # port number


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


def list_to_bonsai_images(iot_dict):
    # list of BonsaiImages to return
    bonsai_images = []

    # parse the iot_dict list
    for x, info in enumerate(iot_dict):

        if (info["Names"] != "edgeHub") and (info["Names"] != "edgeAgent"):
            # check for port
            if "Ports" in info.keys():
                # port format: 'Ports': '0.0.0.0:5005->5000/tcp, :::5005->5000/tcp'
                splitports = info["Ports"]

                if splitports is not None:
                    # split on comma first - 0.0.0.0:5005->5000/tcp
                    splitport_1 = splitports.split(",")[0]
                    # split next on arrow - 0.0.0.0:5005
                    splitport_2 = splitport_1.split("->")[0]
                    # finally split on colon and take last element - 5005
                    port = splitport_2.split(":")[1]
            version = 0
            # split image on slashes
            slashes = info["Image"].split("/")

            # if image tag or no slashes, use the image name
            if slashes is not None and len(slashes) == 1:
                brain_id = info["Image"]
                short_name = brain_id[:9]
            else:
                # if there's a colon in the name, use it for version 
                colon = slashes[-1].split(":")
                if colon and len(colon) > 1:
                    version_split = colon[1].split("-")
                    if version_split is not None:
                        version = version_split[0]
                        brain_id = colon[0]
                        short_name = brain_id[:6] + ":" + version
                    else:
                        brain_id = colon[0]
                        short_name = brain_id[:9]
                else:
                    brain_id = info["Image"]
                    short_name = brain_id[:9]


            bonsai_image = BonsaiImage(
                image=info["Image"],
                brain_id=brain_id,
                version=version,
                short_name=short_name,
                port=int(port),
            )
            bonsai_images.append(bonsai_image)
    return bonsai_images


if __name__ == "__main__":
    print(ps()[0])
