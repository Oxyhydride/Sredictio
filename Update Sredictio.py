"""
Update Sredictio.py

Created on 2019-12-21
Updated on 2019-12-22

Copyright Ryan Kan 2019

Description: A program which obtains the latest RELEASE and updates Sredictio.
"""

# IMPORTS
import json
import math
import os
import re
import zipfile
from shutil import copy, copytree, rmtree
import requests


# FUNCTIONS
def sc(s, v):
    return "".join([chr(c + v) for c in s])


# SECRETS
bs1 = b'DFDSCQ\x16\x11W\x11\x10G?SC\x13MMDJK\x10LHQ@QA\x10\x16\x11\x15TIO\x13NDF\x15\x10\x13\x14IQI\x11MQWCBV\x10SF' \
      b'BW?\x15\x10\x15\x11B\x0f\x13G@GHFK\x10\x10\x11\x16\x11IDBBKE\x11UA\x14WBBXNOH\x0eM\x0eMM\x10EPIPV\x11WRUDFI' \
      b'SX\x12HE\x13GSCMGSDV\x13\x12BF\x15D\x10DF@S\x16CTHMDI\x11\x17RVF?I\x14\x11\x11\x13\x17\x13\x12\x13\x12UCDDD' \
      b'@FQW\x11\x15\x15\x11\x16RQCOI\x12G\x0eLN\x13@\x13EP\x12NSO\x11\x0f\x12A?\x10\x0f\x10\x13D@DD\x14\x17\x12B' \
      b'\x13\x15\x0f@\x13\x0f?@\x11?\x14\x13\x15D@\x0f\x12C\x12@?\x13\x13C@A\x13\x17FEBCI\x11S\x17\x11\x15WPM\x13' \
      b'\x11\x10\x0eURS\x16KQMTG\x10???\x0fCJGE\x17PO@?VHTPEQF@BQ@F\x15HLI?NM@PW\x15\x11\x11K\x17\x0eE?\x11?IHR\x13' \
      b'AWSI@@QN\x15LW\x0eMRL\x11\x10NLMP\x10\x13GSCMGS\x11\x17LD@DV\x13P\x12@WED\x15\x10WT\x13UTUI\x15\x14\x13\x0fG' \
      b'M\x15\x0fO\x10DIQBG\x17\x11\x12DJMGF\x14\x14?\x13UAVDGL\x17\x10\x16\x0fP?@DC\x0fB\x0fOH\x11\x16\x16VONAR\x10F' \
      b'?T\x10\x11\x16'
bs2 = b"\x1a\x04\x00\x0c\x1b\x16J\t\x07EoT\x14S\x01\x02\x01\x02hH\x0fMi\t\x1a\rjJ\x01H\x1cM\x00Oo\rV\x02WjI\x01JkZ" \
      b"\\F@KPRQAVVUSkB\x05J\x1e\x07\x0e\x1e"
bs3 = b'fY"gYUfW\\\x1cf\'[Yl \x14c\'\x1d"[fcid\x1c$\x1dO\'.!&Q'
o2 = int(math.pi * 10 + math.e)
o3 = sc(bs1, o2)
r2 = b"27182818284590452353602874713526624977572470936999595749669676277"
r4 = "5645708485"
r3gex = str(bytes([a ^ b for a, b in zip(bs2, r2)]), "".join([chr(int(r4[i * 2:i * 2 + 2])) for i in range(5)])[::-1])
t = eval(sc(bs3, 12))

# Get latest release
print("Getting latest release's tag...")

header = {"Authorization": 'token %s' % t}
request = requests.get("https://api.github.com/repos/Ryan-Kan/Sredictio/releases/latest", headers=header)
request.raise_for_status()

# Load web page as a dictionary
latestVersionInfo = json.loads(request.text)
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

# If Yes, download latest version
print("Downloading latest version...")

dr = requests.get(latestVersionInfo["zipball_url"], headers=header)
dr.raise_for_status()

open(f"Sredictio-{latestVersion}.zip", "wb").write(dr.content)
print("Done!")

# Extract contents of update package
print("Installing latest version...")

with zipfile.ZipFile(f"Sredictio-{latestVersion}.zip", "r") as zr:
    zr.extractall(".")
    zr.close()

# Check if Update Package was downloaded and extracted correctly
originalFiles = os.listdir(".")
updatePackage = None

for originalFile in originalFiles:
    if re.search(r"(Ryan-Kan-Sredictio)-.+", originalFile):
        updatePackage = originalFile
        break

if updatePackage is None:
    raise FileNotFoundError("Cannot find update package. Abort.")

# Replace current contents with update package's contents
updateFiles = os.listdir("./" + updatePackage)

for updateFile in updateFiles:
    fullFilePath = os.path.join("./" + updatePackage, updateFile)

    if os.path.isfile(fullFilePath):  # Is a file
        print("Updated the file", "./" + updateFile)
        copy(fullFilePath, ".")

    elif os.path.isdir(fullFilePath):  # Is a folder
        print("Updated the directory", "./" + updateFile)
        try:
            rmtree("./" + updateFile)

        except FileNotFoundError:
            pass

        copytree(fullFilePath, "./" + updateFile)

# Remove update packages
os.remove(f"./Sredictio-{latestVersion}.zip")
rmtree("./" + updatePackage)
print("Done!")

# Update version number
open("VERSION", "w").write(latestVersion)
