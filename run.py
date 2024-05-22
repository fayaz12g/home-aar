from extract import *
from script import *
import os
import sys
import SarcLib
import libyaz0
from repack import *
import shutil
import struct

folder_path = r"C:\Users\fayaz\AppData\Roaming\suyu\load\0100000000001000\1\romfs\lyt"

aspect_ratio = 21/9

####################
# BLARC Extraction #
####################

for root, _, files in os.walk(folder_path):
    for file in files:
        if file.lower().endswith(".szs"):
            file_path = os.path.join(root, file)
            print(f"Extracting {file}.")
            extract_blarc(file_path)
            os.remove(file_path)
            
###########################
# Perform Pane Strecthing #
###########################

patch_blarc(aspect_ratio, folder_path)

    
##########################
# Cleaning and Repacking #
##########################

print("Repacking new blarc files. This step may take about 10 seconds")
for root, dirs, _ in os.walk(folder_path):
    if "blyt" in dirs:
        parent_folder = os.path.dirname(root)
        new_blarc_file = os.path.join(parent_folder, os.path.basename(root) + ".szs")
        pack_folder_to_blarc(root, new_blarc_file)
        shutil.rmtree(root) 
