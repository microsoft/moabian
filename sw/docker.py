import subprocess

class BonsaiImage:
    image:            # image     scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-linux-arm32v7
    brainid:          # 'circle'
    version:          # 2 or empty ''
    short_name        # 'circle:2'  (maximum of 9 chars)


# uri = info["Image"]
# n = uri.split(":")[0].split('/')[-1][0:6]
# print(uri)
# v = uri.split(":")[1].split('-')[1][0:2]
# menu_name = n + ":" + v

def ps():
    docker_ps = subprocess.Popen(
        "docker ps --format '{{json .}}'",
        stdout=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout = docker_ps.communicate()[0]
    if docker_ps.returncode == 0:

        json = janky_to_json(stdout)
        print(json)



    # subprocess.PIPE
    foo = janky_to_json()
    list_of_docker_images = rehydrate(foo)
    list_of_bonsai_images = parse_weird_engineering_versions(list_of_docker_images)
    return list_of_bonsai_images

# {} {} {} 
# [ {}, {}, ]


def janky_to_json(stdout)
    # docker ps returns invalid json
    # split the json objects on the newline

    ret = "["
    lines = stdout.splitlines()
    for i, line in enumerate(lines):
        ret += line
        # add comma between each json object
        if i != len(lines) - 1:
            ret += ","

    # Add ending bracket for well-formed json
    ret += "]"
    return(ret)

def json_to_object(json)
        # Load the json objects into a list
        iot_dict = json.loads(_iot_json)

        # parse the list
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
                menu_name = doyourthingjohn(image=info["Image"], tag="")

                # if image tag or no slashes, use the image name
                if slashes is not None and len(slashes) == 1:
                    menu_name = info["Image"]
                else:
                    uri = info["Image"]
                    n = uri.split(":")[0].split('/')[-1][0:6]
                    print(uri)
                    v = uri.split(":")[1].split('-')[1][0:2]
                    menu_name = n + ":" + v

def image_to_string(image)
    return "abby"

