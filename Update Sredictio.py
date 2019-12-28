"""
Update Sredictio.py

Created on 2019-12-21
Updated on 2019-12-29

Copyright Ryan Kan 2019

Description: A program which updates Sredictio.
"""

# IMPORTS
import json
import os
import re
import zipfile
from shutil import copy, copytree, rmtree

import requests

# CODE
# Get latest release's information
print("Getting latest release's tag...")

request = requests.get("https://api.github.com/repos/Ryan-Kan/Sredictio/releases/latest")
request.raise_for_status()

latestVersionInfo = json.loads(request.text)  # Information regarding the latest release

# Get the latest version from the dictionary
latestVersion = latestVersionInfo["tag_name"]

# Get current version
with open("VERSION", "r") as f:
    currentVersion = f.read().strip()
    f.close()

# Check if current version is not the latest version
if currentVersion < latestVersion:
    print(f"A new version, {latestVersion}, is available. (Current Version: {currentVersion})")
    while True:
        print()
        print("Do you want to update the software?")
        response = input("[Y]es or [N]o? ")

        if response.upper() not in ["Y", "N"]:
            print(f'"{response}" is not a valid option. Please enter Y for Yes or N for No.')
            continue

        response = response.upper()
        break

    if response == "N":
        print("Quiting updater...")
        exit()
else:
    print("Latest version is installed. Quiting...")
    exit()

# If Yes, request for the zip file
print("Downloading latest version...")
downloadRequest = requests.get(latestVersionInfo["zipball_url"])
downloadRequest.raise_for_status()

# Write the contents to the update package
open(f"Sredictio-{latestVersion}.zip", "wb").write(downloadRequest.content)
print("Done!")

# Extract contents of update package
print("Installing latest version...")

with zipfile.ZipFile(f"Sredictio-{latestVersion}.zip", "r") as zr:
    zr.extractall(".")
    zr.close()

# Check if the Update Package was downloaded and extracted correctly
originalFiles = os.listdir(".")
updatePackage = None

for originalFile in originalFiles:
    if re.search(r"(Ryan-Kan-Sredictio)-.+", originalFile):
        updatePackage = originalFile
        break

if updatePackage is None:
    raise FileNotFoundError("Cannot find update package. Abort.")

# Delete all files and folders in directory
print("\n!!! THIS FUNCTION WILL DELETE ALL OLD FILES !!!")
input("Press enter to confirm.")

originalFiles.remove(updatePackage)  # We don't want the update package to be removed

for originalFile in originalFiles:
    fullFilePath = os.path.join("./", originalFile)

    if os.path.isfile(fullFilePath):  # Is a file
        print("Deleted the file", "./" + originalFile)
        os.remove(fullFilePath)

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Deleted the folder", "./" + originalFile)
        rmtree("./" + originalFile)

# Add update package's contents to the folder
print("\n!!! INSTALLING NEW FILES !!!")
updateFiles = os.listdir("./" + updatePackage)

for updateFile in updateFiles:
    fullFilePath = os.path.join("./" + updatePackage, updateFile)

    if os.path.isfile(fullFilePath):  # That means that the current package is a file
        print("Added the file", "./" + updateFile)
        copy(fullFilePath, ".")

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Added the folder", "./" + updateFile)
        try:
            rmtree("./" + updateFile)

        except FileNotFoundError:
            pass

        copytree(fullFilePath, "./" + updateFile)

# Remove the update package
rmtree("./" + updatePackage)
print("Done!")

# Update the version number in `VERSION`
open("VERSION", "w").write(latestVersion)
