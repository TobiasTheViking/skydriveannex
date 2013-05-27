#!/usr/bin/env python2
import os
import re
import sys
import json
import time
import inspect
import webbrowser
import cookielib
import urllib
import urllib2

conf = False
version = "0.1.0"
plugin = "skydriveannex-" + version

pwd = os.path.dirname(__file__)
if not pwd:
    pwd = os.getcwd()
sys.path.append(pwd + '/lib')

if "--dbglevel" in sys.argv:
    dbglevel = int(sys.argv[sys.argv.index("--dbglevel") + 1])
else:
    dbglevel = 0

import CommonFunctions as common
import skydrive.api_v5
api = skydrive.api_v5.PersistentSkyDriveAPI.from_conf(pwd + "/skydriveannex.creds")


def login():
    common.log("")
    try:
        ret = api.auth_get_token()
    except:
        url = api.auth_user_get_url()
        webbrowser.open(url, True, True)
        print("Please authenticate in browser")
        time.sleep(1)
        print("")
        url = raw_input('URL after last redirect: ').strip()
        api.auth_user_process_url(url)
        ret = api.auth_get_token()

    common.log('API authorization was completed successfully: ' + repr(ret))

    common.log("res: " + repr(ret), 3)
    if len(ret) == 3:
        common.log("Done")
    else:
        common.log("Failure")
        sys.exit(1)

def postFile(subject, filename, folder):
    common.log("%s to %s - %s" % ( filename, folder[0], subject))
    
    tmp_file = findInFolder(subject, folder)
    if tmp_file:
        common.log("File already exists: " + repr(tmp_file))
        return True
    common.log("BLA: " + repr(folder) + " - " + repr(filename))
    res = api.put(filename, folder, overwrite=True)
    if res:
        common.log("Done: " + repr(res))
    else:
        sys.exit(1)

def findInFolder(subject, folder="me/skydrive"):
    common.log("%s(%s) - %s(%s)" % (repr(subject), type(subject), repr(folder), type(folder)), 0)

    for item in api.listdir(folder):
        common.log("name: " + repr(item["name"]) + " - " + repr(item), 3)
        if item["name"] == subject:
            common.log("Done: " + repr(item["id"]))
            return item["id"]

    common.log("Failure")
    return False

def checkFile(subject, folder):
    common.log(subject)
    global m

    tmp_file = findInFolder(subject, folder)
    if tmp_file:
        common.log("Found: " + repr(tmp_file))
        print(subject)
    else:
        common.log("Failure")

def getFile(subject, filename, folder):
    common.log(subject)
    global m

    tmp_file = findInFolder(subject, folder)
    if tmp_file:
        common.log("tmp_file: " + repr(tmp_file))
        content = api.get(tmp_file)

        saveFile(filename, content, "wb")
        common.log("Done: " + repr(content))
        return True
    common.log("Failure")


def deleteFile(subject, folder):
    common.log(subject)
    global m

    tmp_file = findInFolder(subject, folder)

    if tmp_file:
        res = api.delete(tmp_file)
        common.log("Done")
        return True
    common.log("Failure")

def readFile(fname, flags="r"):
    common.log(repr(fname) + " - " + repr(flags))

    if not os.path.exists(fname):
        common.log("File doesn't exist")
        return False
    d = ""
    try:
        t = open(fname, flags)
        d = t.read()
        t.close()
    except Exception as e:
        common.log("Exception: " + repr(e), -1)

    common.log("Done")
    return d

def saveFile(fname, content, flags="w"):
    common.log(fname + " - " + str(len(content)) + " - " + repr(flags))
    t = open(fname, flags)
    t.write(content)
    t.close()
    common.log("Done")

def createFolder(path="me/skydrive/", folder=""):
    common.log(repr(path) + " - " + repr(folder))

    res = api.mkdir(name=folder, folder_id=path)
    common.log("Done: "+ res["id"])
    return res["id"]

def main():
    global conf
    args = sys.argv

    ANNEX_ACTION = os.getenv("ANNEX_ACTION")
    ANNEX_KEY = os.getenv("ANNEX_KEY")
    ANNEX_HASH_1 = os.getenv("ANNEX_HASH_1")
    ANNEX_HASH_2 = os.getenv("ANNEX_HASH_2")
    ANNEX_FILE = os.getenv("ANNEX_FILE")
    envargs = []
    if ANNEX_ACTION:
        envargs += ["ANNEX_ACTION=" + ANNEX_ACTION]
    if ANNEX_KEY:
        envargs += ["ANNEX_KEY=" + ANNEX_KEY]
    if ANNEX_HASH_1:
        envargs += ["ANNEX_HASH_1=" + ANNEX_HASH_1]
    if ANNEX_HASH_2:
        envargs += ["ANNEX_HASH_2=" + ANNEX_HASH_2]
    if ANNEX_FILE:
        envargs += ["ANNEX_FILE=" + ANNEX_FILE]
    common.log("ARGS: " + repr(" ".join(envargs + args)))

    #ANNEX_HASH_1 = ANNEX_HASH_1 + "-"
    #ANNEX_HASH_2 = ANNEX_HASH_2 + "-"

    conf = readFile(pwd + "/skydriveannex.conf")
    try:
        conf = json.loads(conf)
    except Exception as e:
        common.log("Traceback EXCEPTION: " + repr(e))
        common.log("Couldn't parse conf: " + repr(conf))
        conf = {"folder": "gitannex"}

    common.log("Conf: " + repr(conf), 2)

    login()
    
    folder = findInFolder(conf["folder"])
    if folder:
        common.log("Using folder: " + repr(folder))
        ANNEX_FOLDER = folder + "/"
    else:
        folder = createFolder(folder=conf["folder"])
        common.log("created folder0: " + repr(folder))
        ANNEX_FOLDER = folder + "/"

    if ANNEX_HASH_1:
        folder = findInFolder(ANNEX_HASH_1, ANNEX_FOLDER)
        if folder:
            common.log("Using folder1: " + repr(folder))
            ANNEX_FOLDER = folder + "/"
        else:
            folder = createFolder(ANNEX_FOLDER, ANNEX_HASH_1)
            common.log("created folder1: " + repr(folder))
            ANNEX_FOLDER = folder + "/"

    if ANNEX_HASH_2:
        folder = findInFolder(ANNEX_HASH_2, ANNEX_FOLDER)
        if folder:
            common.log("Using folder2: " + repr(folder))
            ANNEX_FOLDER = folder + "/"
        else:
            folder = createFolder(ANNEX_FOLDER, ANNEX_HASH_2)
            common.log("created folder2: " + repr(folder))
            ANNEX_FOLDER = folder + "/"

    if "store" == ANNEX_ACTION:
        postFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER)
    elif "checkpresent" == ANNEX_ACTION:
        checkFile(ANNEX_KEY, ANNEX_FOLDER)
    elif "retrieve" == ANNEX_ACTION:
        getFile(ANNEX_KEY, ANNEX_FILE, ANNEX_FOLDER)
    elif "remove" == ANNEX_ACTION:
        deleteFile(ANNEX_KEY, ANNEX_FOLDER)
    else:
        setup = '''
Please run the following command in your annex directory
git config annex.skydrive-hook '/usr/bin/python2 %s/skydriveannex.py'
git annex initremote skydrive type=hook hooktype=skydrive encryption=%s
git annex describe skydrive "the skydrive library"
''' % (os.getcwd(), "shared")
        print setup

        saveFile(pwd + "/skydriveannex.conf", json.dumps(conf))
        sys.exit(1)

t = time.time()
common.log("START")
if __name__ == '__main__':
    main()
common.log("STOP: %ss" % int(time.time() - t))
