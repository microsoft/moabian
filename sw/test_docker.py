# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import docker

# To run on moab:
#   pip3 install pytest
#   cd moab/sw
#   pytest test_docker.py

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

# mult slashes, 1 colon, mult dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-linux-arm32v7
def test_mult_slashes_1_colon_mult_dashes():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/m-circle-1:2-linux-arm32v7"
    assert docker.get_image_info(image_name, 0).short_name == "m-circle-1:2"


# mult slashes, 1 colon, no dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2
def test_mult_slashes_1_colon_no_dash():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2"
    assert docker.get_image_info(image_name, 0).short_name == "circle:2"


# mult slashes, 1 colon, 1 dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-arm32v7
def test_mult_slashes_1_colon_1_dash():
    image_name = (
        "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2-arm32v7"
    )
    assert docker.get_image_info(image_name, 0).short_name == "circle:2"


# mult slashes, mult colon, no dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:er
def test_mult_slashes_mult_colon_no_dash():
    image_name = (
        "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:er"
    )
    assert docker.get_image_info(image_name, 0).short_name == "circle:2"


# mult slashes, mult colon, mult dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32-v7
def test_mult_slashes_mult_colon_mult_dash():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32-v7"
    assert docker.get_image_info(image_name, 0).short_name == "circle:2"


# mult slashes, mult colon, 1 dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32
def test_mult_slashes_mult_colon_1_dash():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle:2:linux-arm32"
    assert docker.get_image_info(image_name, 0).short_name == "circle:2"


# mult slashes, no colon, no dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle
def test_mult_slashes_no_colon_no_dash():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle"
    assert docker.get_image_info(image_name, 0).short_name == "circle"


# mult slashes, no colon, 1 dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux
def test_mult_slashes_no_colon_1_dash():
    image_name = (
        "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux"
    )
    assert docker.get_image_info(image_name, 0).short_name == "circle-li"


# mult slashes, no colon, mult dash
# scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux-arm32v7
def test_mult_slashes_no_colon_multi_dash():
    image_name = "scotstanws.azurecr.io/d83f2142-1c3c-4ae4-84fa-4e9ff3aa5ed9/circle-linux-arm32v7"
    assert docker.get_image_info(image_name, 0).short_name == "circle-li"


# 1 slash, no colon, no dash
# moab/brain
def test_1_slash_no_colon_no_dash():
    image_name = "moab/brain"
    assert docker.get_image_info(image_name, 0).short_name == "brain"


# 1 slash, no colon, 1 dash
# moab/brain-linux
def test_1_slash_no_colon_1_dash():
    image_name = "moab/brain-linux"
    assert docker.get_image_info(image_name, 0).short_name == "brain-lin"


# 1 slash, no colon, mult dash
# moab/brain-linux-v32
def test_1_slash_no_colon_mult_dash():
    image_name = "moab/brain-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "brain-lin"


# 1 slash, 1 colon, no dash
# moab/brain:3
def test_1_slash_1_colon_no_dash():
    image_name = "moab/brain:3"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, 1 colon, 1 dash
# moab/brain:3-linux
def test_1_slash_1_colon_1_dash():
    image_name = "moab/brain:3-linux"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, 1 colon, mult dash
# moab/brain:3-linux-v32
def test_1_slash_1_colon_mult_dash():
    image_name = "moab/brain:3-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, mult colon, no dash
# moab/brain:3:3
def test_1_slash_mult_colon_no_dash():
    image_name = "moab/brain:3:3"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, 1 colon, 1 dash
# moab/brain:3:3-linux
def test_1_slash_mult_colon_no_dash():
    image_name = "moab/brain:3:3-linux"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, 1 colon, multi dash
# moab/brain:3-linux-v32
def test_1_slash_1_colon_multi_dash():
    image_name = "moab/brain:3-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, multi colon, no dash
# moab/brain:3:3
def test_1_slash_multi_colon_no_dash():
    image_name = "moab/brain:3:3"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, multi colon, 1 dash
# moab/brain:3:3-linux
def test_1_slash_multi_colon_1_dash():
    image_name = "moab/brain:3:3-linux"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


# 1 slash, multi colon, multi dash
# moab/brain:3:3-linux-v32
def test_1_slash_multi_colon_multi_dash():
    image_name = "moab/brain:3:3-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "brain:3"


####

# no slash, no colon, no dash
# den1
def test_no_slash_no_colon_no_dash():
    image_name = "den1"
    assert docker.get_image_info(image_name, 0).short_name == "den1"


# no slash, no colon, 1 dash
# den1-linux
def test_no_slash_no_colon_1_dash():
    image_name = "den1-linux"
    assert docker.get_image_info(image_name, 0).short_name == "den1-linu"


# no slash, no colon, mult dash
# den1-linux-v32
def test_no_slash_no_colon_mult_dash():
    image_name = "den1-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "den1-linu"


# no slash, 1 colon, no dash
# moab/brain:3
def test_no_slash_1_colon_no_dash():
    image_name = "den1:3"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


# no slash, 1 colon, 1 dash
# den1:3-linux
def test_no_slash_1_colon_1_dash():
    image_name = "den1:3-linux"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


# no slash, 1 colon, mult dash
# moab/brain:3-linux-v32
def test_no_slash_1_colon_mult_dash():
    image_name = "den1:3-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


# no slash, mult colon, no dash
# den1:3:4
def test_no_slash_mult_colon_no_dash():
    image_name = "den1:3:4"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


# no slash, 1 colon, 1 dash
# den1:3:4-linux
def test_no_slash_mult_colon_1_dash():
    image_name = "den1:3:4-linux"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


# no slash, 1 colon, multi dash
# moab/brain:3-linux-v32
def test_no_slash_multi_colon_multi_dash():
    image_name = "den1:3:4-linux-v32"
    assert docker.get_image_info(image_name, 0).short_name == "den1:3"


#     = image name no slash

#       = no colon no dash - den1
#       = no colon 1 dash - den1-linux
#       = no colon more than 1 dash - v2-02-rg

#       = 1 colon no dash - den1:v2
#       = 1 colon 1 dash - den1:3-linux
#       = 1 colon more than 1 dash - den1:v2-02-rg

#       = more than 1 colon no dash - den1:v2:hi
#       = more than 1 colon 1 dash - den1:v2:23-rg
#       = more than 1 colon more than 1 dash - den1:v2:-02-rg