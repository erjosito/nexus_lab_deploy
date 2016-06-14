Nexus Lab Deployment Tool
=========================

#### This is a small tool to easily snap and deploy configurations of multiple Nexus switches through its REST API. 

## Table of Contents
  
  * [Introduction](#introduction)
  * [Requirements](#requirements)
  * [Getting Started] (#getting-started)
  * [JSON Configuration Files] (#json-configuration-files)
	* [Snap JSON] (#snap-json)
	* [Deploy JSON] (#deploy-json)	
  * [Log File] (#log-file)
  * [Changelog] (#changelog)


# Introduction
This tool allows to quickly deploy and snap configurations from a lab environment. Deployments are stored in a JSON configuration file together with the running configurations as text files.

# Requirements
It is recommended to use this tool on a Linux machine running Python 2.7. Other OS and Python versions might need some code changes.

You need to install the following software to run this toolkit:
* [Python2](https://www.python.org/)
* [pyntc](https://github.com/networktocode/pyntc)

# Getting Started
You can run this tool by executing the `nexus_lab_deploy.py` file. Now you either have to issue the `snap` or `deploy` command.  
The `snap` command will backup all running configurations from the switches defined in a JSON configuration file and save them locally on your machine. At the same time, a new JSON configuration file will be created that allows you to easily deploy the configurations back on all your switches.  
The `deploy` command pushes configurations to multiple switches which are defined in a JSON configuration file. Please keep in mind that after a configuration is pushed out on a switch, the device has to reboot and it might take a while until the script will continue (notifications about device reachability will appear on the CLI though).

# JSON Configuration Files
Parameters such as IP addresses, username, passwords and locations to save/load running configurations are defined in JSON files. The files `examples/snap.json` and `examples/deploy.json` show the structure of those files.

## Snap JSON
The snap function backups all running configurations from a lab environment and creates a new deployment JSON file to easily redeploy the lab environment. To snap a lab, you have to set a JSON file that defines all information to snap the lab environment. You can modify the JSON file to define your own lab environment. Just make sure that you do not break the JSON syntax. The content of the JSON files looks like this:

```
{
    "path": "C:\\Users\\MyUser\\Desktop", 
    "lab_name": "MyLab", 
    "switches": [
        {            
			"target": "198.18.134.140", 
            "user": "admin", 
            "pw": "pw12345"
        }, 
		{            
			"target": "198.18.134.141", 
            "user": "admin", 
            "pw": "pw12345"
        }
    ]
}
```

`path`: Folder where all the running configurations and the deployment JSON configuration file will be saved. Path can be absolute or relative.  

`lab_name`: Name of the lab environment.  

`switches`: List of IP addresses or hostnames and their usernames and passwords. Snapping will save the running configurations of all switches defined in this list. You can easily add more switches by extending this list with new IP addresses and login credentials.  

## Deploy JSON
The deploy function gets a deployment JSON configuration file and pushes all configurations to all switches which are defined in the JSON file. You can either manually create this deployment file or you can use the snap function which automatically creates a deployment configuration based on your current lab environment. The content of the JSON files looks like this:

```
{
    "lab_name": "MyLab", 
	"date": "2016-06-14", 
    "configurations": [
        {
            "cfg": "C:\\Users\\MyUser\\Desktop\\MyLab\\198.18.134.140.cfg",
            "target": "198.18.134.140",
            "user": "admin",
			"pw": "pw12345"
        }, 
        {
            "cfg": "C:\\Users\\MyUser\\Desktop\\MyLab\\198.18.134.141.cfg",
            "target": "198.18.134.141",
            "user": "admin",
			"pw": "pw12345"
        }
    ]
}
```

`lab_name`: Name of the lab environment.  

`date`: Date when the lab environment was created.  

`configurations`: List of host information and paths to the configuration files that will be pushed out to the devices. Path can be absolute or relative. 

# Log File
In case there will be an error, the script will automatically create a log file which will contain more detail information about the execution of the script. The log file is named `nexus_lab_deploy.log` and will be stored in the same folder where the script is executed.

# Changelog

## v0.1 (2016-06-14)

Initial release
