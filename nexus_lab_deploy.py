#!/usr/bin/env python
#
#     Lab Deploy Tool
#       v0.1
#
#     Christian Jaeckel (chjaecke@cisco.com)
#       June 2016
#
#     This tool allows to quickly deploy and snap
#       configurations from a lab or even production
#       deployments. Deployments are stored in a
#       JSON configuration file together with the
#       running configurations as text files.
#
#     WARNING:
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.
#
from nxapi_wrapper import nxapi_wrapper
from datetime import date
import os
import json
import logging

def deploy(path):
    """
    Deploys configurations on several switches which are defined in a JSON configuration file.

    :param path: Absolute or relative path to the JSON configuration file.
    """

    logging.debug("Call deploy(path)")
    logging.debug("Argument path = %s", path)

    json_cfg = open_json(path)

    debug_print("Start deploying lab.")

    count = 1
    cfgs = json_cfg["configurations"]

    for cfg in cfgs:

        host = cfg["target"]
        user = cfg["user"]
        pw = cfg["pw"]

        debug_print("Start pushing configuration %s of %s." % (count, len(cfgs)))
        debug_print("Target: %s" % host)

        try:
            # Open connection to host and push configuration to switch.
            wrapper = nxapi_wrapper(host, user, pw)
            wrapper.set_running_config(cfg["cfg"])

        except Exception as e:
            logging.critical("Failed to push configuration to target: %s")
            logging.critical(str(e))
            print_error()
            return

        debug_print("Target response received: %s" % host)

        count += 1

    debug_print("Pushing configurations successful")


def snap(path):
    """
    Fetches all running configurations which are defined in a JSON , stores them locally on the machine and creates JSON configurations file for
    the deployment.

    :param path: Absolute or relative path to the JSON configuration file.
    """
    logging.debug("Call snap(path)")
    logging.debug("Argument path = %s", path)

    json_cfg = open_json(path)

    path = json_cfg["path"]
    name = json_cfg["lab_name"]

    debug_print("Start snapping to %s" % path)

    path = os.path.join(path, name)
    os.makedirs(path)

    json_snap = {}
    json_snap["name"] = name
    json_snap["date"] = date.today().isoformat()
    json_snap["configurations"] = json_cfg["switches"]

    for cfg in json_cfg["switches"]:

        try:
            logging.debug("Start to backup target: %s" % cfg["target"])
            debug_print("Start to backup target: %s" % cfg["target"])

            # Open connection to host and download configuration from switch.
            wrapper = nxapi_wrapper(cfg["target"], cfg["user"], cfg["pw"])
            cfg["cfg"] = os.path.join(path, cfg["target"] + ".cfg")
            wrapper.backup_running_config(cfg["cfg"])
            debug_print("Finished to backup target: %s" % cfg["target"])

        except Exception as e:
            logging.critical("Failed to backup configuration from target: %s" % cfg["target"])
            logging.critical(str(e))
            print_error()
            return

    debug_print("Save configurations files.")

    save_json(json_snap, os.path.join(path, name + ".json"))


def cli_start():
    """
    Start hook for CLI interface.
    """

    # Initiate logger
    logging.basicConfig(
        filename='nexus_lab_deploy.log',
        level=logging.DEBUG,
        filemode='w',
        format='%(asctime)s|%(levelname)s:%(message)s',
        datefmt='%m/%d/%Y %I:%M:%S'
    )

    print("##########################################")
    print("####                                  ####")
    print("####  Nexus Lab Deployment Tool       ####")
    print("####                                  ####")
    print("####  Version: 0.1                    ####")
    print("####  Date: 2016-06-15                ####")
    print("####  Developer: Christian Jaeckel    ####")
    print("####  Email: chjaecke@cisco.com       ####")
    print("####                                  ####")
    print("##########################################")
    print("")

    cmd = ""
    while not cmd == "snap" or not cmd == "deploy":
        cmd = raw_input("Enter if you want to deploy or snap your lab environment [\"snap\" or \"deploy\"]: ")

        if cmd == "snap" or cmd == "deploy":
            break
        else:
            print("Unknown command. Please enter either \"snap\" or \"deploy\"")

    print("Gathering information to %s lab ..." % cmd)

    path = raw_input("Enter JSON %s configuration file: " % cmd)

    if cmd == "snap":
        snap(path)
    else:
        deploy(path)

    print("Finished.")


def save_json(json_obj, path):
    try:
        with open(path, 'w') as outfile:
            json.dump(json_obj, outfile, indent=4)
            outfile.close()

    except Exception as e:
        logging.warning("Failed to save JSON configuration file.")
        logging.critical(str(e))
        print_error()
        return


def open_json(path):
    try:
        with open(path) as data_file:
            json_cfg = json.load(data_file)

        if json_cfg is None:
            raise Exception("Could not open file.")

    except Exception as e:
        logging.warning("Failed to open JSON configuration file.")
        logging.critical(str(e))
        print_error()
        return

    return json_cfg


def debug_print(msg):
    print(msg)
    logging.debug("Console: %s", msg)

def print_error():
    print("Error. Please check log file for more information.")

def main():
    """
    Main method to start this configuration extraction tool.
    """
    cli_start()

if __name__ == '__main__':
    main()