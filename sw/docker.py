import subprocess
import json
import sys
from dataclasses import dataclass

@dataclass
class BonsaiImage:
    image: str            # image     scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-linux-arm32v7
    brain_id: str         # 'circle'
    version: str         # 2 or empty ''
    short_name: str       # 'circle:2'  (maximum of 9 chars if no version else truncated to 6 chars)
    port: int             # port number

def ps():
    docker_ps = subprocess.Popen(
        "docker ps --format '{{json .}}'",
        stdout=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout = docker_ps.communicate()[0]

    if docker_ps.returncode == 0:    
        json = reformat_json(stdout)
        #print(json)
        docker_images = json_to_object(json)
        bonsai_images = list_to_bonsai_images(docker_images)
        return bonsai_images

    # subprocess.PIPE
    # foo = janky_to_json()
    # list_of_docker_images = rehydrate(foo)
    # list_of_bonsai_images = parse_weird_engineering_versions(list_of_docker_images)
    # return list_of_bonsai_images

    # {} {} {} 
    # [ {}, {}, ]

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
    return(json)

def json_to_object(json_s):         
    # Load the json objects into a list
    iot_dict = json.loads(json_s)
    return iot_dict       

def list_to_bonsai_images(iot_dict):
    #list of BonsaiImages to return
    bonsai_images = []

    # parse the iot_dict list
    for x, info in enumerate(iot_dict):

        if (
            (info["Names"] != "edgeHub")
            and (info["Names"] != "edgeAgent")
        ):
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

            # split image on slashes
            slashes = info["Image"].split("/")

            # turn docker "URI" style image into a suitable string
            #menu_name = doyourthingjohn(image=info["Image"], tag="")

            # if image tag or no slashes, use the image name
            if slashes is not None and len(slashes) == 1:
                image = info["Image"]
                brain_id = image
                short_name = brain_id[:9]
            else:
                # split on colon
                image = info["Image"]
                colon = slashes[-1].split(":")
                version_split = colon[1].split("-")
                if version_split is not None:
                    version = version_split[0]
                    brain_id = colon[0]
                    short_name = brain_id[:6] + ":" + version
                else:
                    brain_id = colon[0]
                    short_name = brain_id[:9]

            bonsai_image = BonsaiImage(
                            image=image, 
                            brain_id=brain_id,
                            version=version,
                            short_name=short_name,
                            port=int(port),     
            )
            bonsai_images.append(bonsai_image)
    return bonsai_images

if __name__ == "__main__":
    print(ps()[0])