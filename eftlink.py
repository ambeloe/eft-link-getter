import re
import sys
import json
import zlib
import requests

# url that has all the metadata of verisons (compressed using zlib)
metaUrl = "https://launcher.escapefromtarkov.com/launcher/GetPatchList?launcherVersion=0&branch=live"

resp = requests.get(metaUrl)
decompressed = zlib.decompress(resp.content)
jsondat = json.loads(decompressed)["data"]


# convert update links to a full client link
# dont use unless you only have an update string because its probably slower
def update_str2client_str(uurl):
    return re.sub("[0-9]\.[0-9][0-9]\.[0-9]\.[0-9][0-9][0-9][0-9]-", "",
                  uurl.replace("ClientUpdates", "ClientDistribs").replace(".update", ".zip"))


# get a client or update link for the requested version
# version_str: string; a tarkov-y version number (ex:"0.12.7.8753")
# link_type: int; 0 = update link, 1 = client link
# checksum: boolean; False = returns url string, True = returns tuple (link, hash)
# returns a string containing the requested link, a tuple containing an update link and a md5 hash, or an error message
def get_link(version_str, link_type=1, checksum=False):
    for ver in jsondat:
        if ver["Version"] == version_str:
            url = ver["DownloadUri"]
            if link_type == 0:
                if checksum:
                    return url, ver["hash"]
                else:
                    return url
            else:
                return url.replace("ClientUpdates", "ClientDistribs").replace(ver["FromVersion"].join("-"), "").replace(
                    ".update", ".zip")
    return "the specified version could not be found"


# returns the latest version string
def get_latest_version():
    return jsondat[0]["Version"]


# writes the whole response to disk in a file called resp.json
def dump():
    with open("resp.json", "w") as pog:
        pog.write(json.dumps(json.loads(decompressed), indent=2, separators=(',', ': ')))


# usage: python eftlink.py arg1 arg2
# arg1: version string or "latest"
# arg2: "update" or "client"
# if arg1 is "dump" then the program will dump the whole response after decompression to disk (resp.json)
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "dump":
        dump()
        print("dumped response data to resp.log")
    elif len(sys.argv) == 3:
        if sys.argv[1] == "latest":
            if sys.argv[2] == "update":
                print(get_link(get_latest_version(), link_type=0))
            elif sys.argv[2] == "client":
                print(get_link(get_latest_version()))
            else:
                print("invalid link type")
        else:
            if sys.argv[2] == "update":
                print(get_link(sys.argv[1], link_type=0))
            elif sys.argv[2] == "client":
                print(get_link(sys.argv[1]))
            else:
                print("invalid link type")
    else:
        print("invalid argument/s")
