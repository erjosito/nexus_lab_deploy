#!/usr/bin/env python
#
#     Lab Deploy Tool
#       v0.1
#
#     Christian Jaeckel (chjaecke@cisco.com)
#       June 2016
#
#     Code contributed by Jose Moreno (josemor@cisco.com)
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
import argparse
import cmd2
import sys

class labDeployCli (cmd2.Cmd):

	prompt = 'lab# '
	switches = []
	parallel = False
	labfile = ""
	intro = """
    ##########################################
    ####                                  ####
    ####  Nexus Lab Deployment Tool       ####
    ####                                  ####
    ####  Version: 0.1                    ####
    ####  Date: 2016-06-15                ####
    ####  Developer: Christian Jaeckel    ####
    ####  Email: chjaecke@cisco.com       ####
    ####                                  ####
    ##########################################
    
    Type 'help' to get a list of commands
	"""
	

	def do_snap (self, line):
		'''
		Snapshot the configs in a lab. Switches and credentials are specified with a lab file.
		  If no lab file is specified, info is taken out of the active lab file
		Syntax: snap [lab-file.json]
		Example:
			  snap
			  snap path_to_my_lab_file.json
		'''
		args = line.split()
		if len (args) < 1:
			mylabfile = self.labfile
		else:
			try:
				mylabfile = args[0]
			except:
				print "Invalid parameters. Type 'help snap' for help"
				return False
			# If the user specified a file, we load that file directly
			try:
				with open (mylabfile) as json_file:
					self.switches = json.load (json_file)
					self.labfile = mylabfile
					# Update prompt with filename
					filename = os.path.basename(mylabfile)
					fileshort = filename.split (".")[0]
					self.prompt = fileshort + "# "
			except:
				print "Error loading data from %s" % filename

		answer = query_yes_no("Are you sure you want to download %s configs to %s?" % (str(len(self.switches["configurations"])), os.path.dirname(mylabfile)), default="yes")
		if answer == False:
			return False

		# Store the current lab, in case the user added or removed switches
		self.savelabfile(mylabfile)
		# Go and fetch the config, and update the self.switches variable with new config files
		self.switches = snap(mylabfile)
		# Store the current lab with the new config files returned from snap
		#self.savelabfile(mylabfile)

	def do_deploy (self, line):
		'''
		Deploys the configs in a lab. Switches, credentials, and configs to be deployed
		    are specified with a lab file.
		Syntax: deploy <lab-file.json>
		Example:
			  deploy
			  deploy path_to_my_lab_file.json
		'''
		args = []
		args = line.split()
		if len (args) < 1:
			mylabfile = self.labfile
		else:
			try:
				mylabfile = args[0]
			except:
				print "Invalid parameters. Type 'help deploy' for help"
				return False
			try:
				with open (mylabfile) as json_file:
					self.switches = json.load (json_file)
					self.labfile = mylabfile
					# Update prompt with filename
					filename = os.path.basename(mylabfile)
					fileshort = filename.split (".")[0]
					self.prompt = fileshort + "# "
			except:
				print "Error loading data from %s" % filename

		if self.parallel:
			print "Deploy mode set to Parallel"
		else:
			print "Deploy mode set to Serial"
		answer = query_yes_no("Are you sure you want to deploy %s configs to your lab?" % str(len(self.switches["configurations"])), default="no")
		if answer == False:
			return False

		# Store the current lab, in case the user added or removed switches
		self.savelabfile(mylabfile)
		# Deploy configs
		deploy(mylabfile, self.parallel)

	def do_showdeploymode (self, line):
		'''
		Shows the deploy mode (serial or parallel)
		Syntax: showdeploymode
		Example:
			  showdeploymode
		'''
		if self.parallel:
			print "Parallel"
		else:
			print "Serial"

	def do_setdeploymode (self, line):
		'''
		Sets the deploy mode to serial or parallel
		Syntax: setdeploymode parallel|serial
		Example:
			  setdeploymode parallel
		'''
		args = line.split()
		if len (args) < 1:
			print "Not enough arguments provided, please type 'help addswitch' for information on this command"
			return False
		else:
			mymode = args[0]
		# Change the mode
		if mymode=="parallel":
			self.parallel = True
		elif mymode == "serial":
			self.parallel = False
		else:
			print "Please use either 'parallel' or 'serial'"
	
	def do_setlabdesc (self, line):
		'''
		Sets the Lab description
		Syntax: setlabdesc <lab description>
		Example:
			  setlabdesc VXLAN configuration
		'''

		self.switches['description'] = line	

		
	def do_findfiles (self, line):
		'''
		Finds json file in the current directory, or in a specified directory.
		Syntax: findfiles [directory]
		Example:
			  deploy path_to_my_lab_file.json
		'''
		args = line.split()
		if len (args) < 1:
			dir = os.getcwd()
		else:
			dir = args[0]

		for root, dirs, files in os.walk(dir):
			for file in files:
				if file.endswith(".json"):
					 print(os.path.join(root, file))	

	def do_showlabs (self, line):
		'''
		Finds json files in the current directory, or in a specified directory, and show
		    information contained there
		Syntax: findfiles [directory]
		Example:
			  deploy path_to_my_lab_file.json
		'''
		args = line.split()
		if len (args) < 1:
			dir = os.getcwd()
		else:
			dir = args[0]

		for root, dirs, files in os.walk(dir):
			for file in files:
				if file.endswith(".json"):
					thisfile = os.path.join(root, file)
					print(thisfile)
					with open (thisfile) as json_file:
						theseswitches = json.load (json_file)
					self.showlab (theseswitches)
					print ""


	def do_loadlab (self, filename):
		'''
		Load the lab definitions from a file in JSON format (previously saved with savelab)
		Example: loadlab mylab.json
		'''
		try:
			with open (filename) as json_file:
				self.switches = json.load (json_file)
				self.labfile = filename
				# Update prompt with filename
				filename = os.path.basename(filename)
				fileshort = filename.split (".")[0]
				self.prompt = fileshort + "# "
		except:
			print "Error loading data from %s" % filename

	def do_showlab (self, line):
		'''
		Show the switches configured in the loaded lab file
		Example:  showlab
		'''
		#print json.dumps (self.switches)
		print "Filename   : %s" % self.labfile
		self.showlab (self.switches)

	def showlab (self, switches):
		try:
			print "Date       : %s" % switches['date']
			print "Name       : %s" % switches['name']
			print "Description: %s" % switches['description']
		except:
			pass
		print ""
		print "Switch       Username     Password     Config"
		print "======       ========     ========     ======"
		for switch in switches['configurations']:
			print ('{:<13}{:<13}{:<13}{:<15}'.format(switch['target'], switch['user'], switch['pw'], switch['cfg']))


	def do_addswitch (self, line):
		'''
		Add a switch to the list of managed devices
		Syntax: addswitch <switch_name/ip> <username> <password>
		Example:
			  addswitch n9k-1 admin cisco123
		'''
		args = line.split()
		if len (args) < 3:
			print "Not enough arguments provided, please type 'help addswitch' for information on this command"
			return False
		try:
			target = args[0]
			usr    = args[1]
			pwd    = args[2]
		except:
			print "Invalid parameters. Type 'help addswitch' for help"
			return False

		newswitch = {"pw" : pwd, "user" : usr, "target" : target, "cfg" : ""}
		self.switches['configurations'].append (newswitch)
		
	def do_removeswitch (self, line):
		'''
		Remove a switch from the list of managed devices
		Syntax: removeswitch <switch_name/ip>
		Example:
			  removeswitch n9k-1
		'''
		args = line.split()
		if len (args) < 1:
			print "Not enough arguments provided, please type 'help addswitch' for information on this command"
			return False
		try:
			mytarget = args[0]
		except:
			print "Invalid parameters. Type 'help removeswitch' for help"
			return False

		for i in range (0, len(self.switches['configurations'])):
			if self.switches['configurations'][i]['target'] == mytarget:
				self.switches['configurations'].pop (i)
				return
		#If we arrive here, we did not find the target in the list
		print "Target %s not found in the current lab configuration" % mytarget

	def do_savelab (self, line):
		'''
		Save the switch definitions to a file in JSON format. If no argument specified,
		    saves to the current location
		Example: savelab my_lab.json
		'''
		args = line.split()
		if len (args) < 1:
			answer = query_yes_no("Are you sure you want to overwrite the existing lab file?", default="no")
			if answer == False:
				return False
			else:
				mylabfile = self.labfile
		else:
			mylabfile = args[0]
			
		self.savelabfile (mylabfile)
		# Update the labfile variable
		self.labfile = mylabfile
			

	def savelabfile (self, filename):
		jsonstring = json.dumps(self.switches)
		#print "Saving string %s" % jsonstring
		try:
			with open (filename, "w") as mylabfile:
				mylabfile.write (jsonstring)
		except Exception as e:
			print "Error writing to %s" % filename
			#print e


	def default (self, arg):
		print ('Whaaaaat??? Type help for help (thank you Captain Obvious!)')


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def deploy(path, parallel=True):
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
			if parallel:
				wrapper.set_running_config(cfg["cfg"], True, False)
			else:
				wrapper.set_running_config(cfg["cfg"], True, True)
		except Exception as e:
			logging.critical("Failed to push configuration to target: %s")
			logging.critical(str(e))
			print_error()
			return

		if parallel:
			debug_print("Switch reloaded: %s" % host)
		else:
			debug_print("Target response received: %s" % host)

		count += 1

	# If we were reloading in parallel, now we need to wait for the switches to come back
	if parallel:
		count = 1
		for cfg in cfgs:

		   host = cfg["target"]
		   user = cfg["user"]
		   pw = cfg["pw"]

		   debug_print("Waiting for switch %s of %s to come back." % (count, len(cfgs)))
		   debug_print("Target: %s" % host)

		   try:
			   # Open connection to host and push configuration to switch.
			   wrapper = nxapi_wrapper(host, user, pw)
			   wrapper.set_running_config(cfg["cfg"], False, True)
		   except Exception as e:
			   logging.critical("Switch %s is not coming back!" % host)
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
	logging.debug("Call snap(%s)" % path)

	json_cfg = open_json(path)

	labname = json_cfg["name"]

	dir = os.path.dirname (path)
	file = os.path.basename (path)

	debug_print("Start snapping to %s" % dir)

	json_snap = {}
	try:
		json_snap["name"] = labname
		json_snap["date"] = date.today().isoformat()
		json_snap["configurations"] = json_cfg["configurations"]
		json_snap["description"] = json_cfg["description"]
	except:
		pass

	for cfg in json_cfg["configurations"]:
		try:
			logging.debug("Start to backup target: %s" % cfg["target"])
			debug_print("Start to backup target: %s" % cfg["target"])
			# Open connection to host and download configuration from switch.
			wrapper = nxapi_wrapper(cfg["target"], cfg["user"], cfg["pw"])
			cfg["cfg"] = os.path.join(dir, cfg["target"] + ".cfg")
			wrapper.backup_running_config(cfg["cfg"])
			debug_print("Finished to backup target: %s to %s" % (cfg["target"], cfg["cfg"]))
		except Exception as e:
			logging.critical("Failed to backup configuration from target: %s" % cfg["target"])
			logging.critical(str(e))
			print_error()
			return False
	return json_snap
	#save_json(json_snap, os.path.join(path, name + ".json"))


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
    #cli_start()
    labDeployCli().cmdloop()

if __name__ == '__main__':
    main()