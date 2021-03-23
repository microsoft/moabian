# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Build Menu List

Builds the menu list for menu.py based on dock_compose information
"""
import os
import yaml
import sys

this = sys.modules[__name__]
this.service = ""
this.image = ""
this.menu_name = ""
this.port = 0
this.container_name = ""
this.custom_menu_list = ""

def getFromDict(dataDict, mapList):
    for k in mapList: dataDict = dataDict[k]
    return dataDict

def build_menu_list():
    list_1 = "        MenuOption(\n            name=\"Joystick\",\n            closure=joystick_controller,\n            kwargs={},\n            is_controller=True,\n        ),\n        MenuOption(\n            name=\"PID\",\n            closure=pid_controller,\n            kwargs={},\n            is_controller=True,\n        ),\n"
    list_2 = "        MenuOption(\n            name=\"Calibrate\",\n            closure=calibrate_controller,\n            kwargs={\n                \"env\": env,\n                \"pid_fn\": pid_controller(),\n                \"calibration_file\": \"bot.json\",\n            },\n            is_controller=False,\n        ),\n        MenuOption(\n            name=\"Calib Info\",\n            closure=info_config_controller,\n            kwargs={\"env\": env},\n            is_controller=False,\n            require_servos=False,\n        ),\n        MenuOption(\n            name=\"Bot Info\",\n            closure=info_screen_controller,\n            kwargs={\"env\": env},\n            is_controller=False,\n            require_servos=False,\n        ),\n"
    menu_list = list_1 + build_custom_menu_list() + list_2
    return menu_list

def build_custom_menu_list():
    dc_file = "../docker-compose.yml"
    if os.path.isfile(dc_file):
        with open(dc_file, 'r') as ymlfile:
            docker_compose = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    # limit to services node in docker compose
    services = getFromDict(docker_compose,["services"])
    
    for service, info in services.items():
        this.service = service

        for key in info:
            if key == 'image':
                this.image = info['image']
            if key =='container_name':
                this.container_name = info['container_name']  
            if key == 'ports':
                #dc ports is in form [500x:5000]
                splitports = info['ports']
                #we need 500x so split on colon
                ports = splitports[0].split(":")
                #assign the split port info to the var
                this.port = ports[0]

        #  if container name missing - name comes from image 
        if this.container_name == "": 
            slashs = this.image.split("/")
            # moab/brain has no colon so just split slash
            if slashs is not None and len(slashs) == 1:
                this.menu_name = this.image
            else:
                #split the tag from the colon
                colon = slashs[-1].split(":")
                this.menu_name = colon[0]
        else:
            this.menu_name = this.container_name          

        this.custom_menu_list += str(f"        MenuOption(\n            name=\"{this.menu_name}\",\n            closure=brain_controller,\n            kwargs={{\"port\": {this.port}}},\n            is_controller=True,\n        ),\n")
        this.container_name = ""
    return this.custom_menu_list