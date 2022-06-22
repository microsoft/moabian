import os
import sys

# getting the name of the directory
# where the this file is present.
parent = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
  
# Getting the parent directory name
# where the current directory is present.
# print(f"*** Source __file__: {__file__}")
# print(f"Source folder:   {os.path.dirname(os.path.realpath(__file__))}")
# print(f"Parent folder:   {parent}")
# print(f"Your CWD:        {os.getcwd()}")
# assert(parent == "/home/pi/moab/sw")
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)
