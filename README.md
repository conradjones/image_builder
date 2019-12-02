# Image Builder

Uses Winstall (https://github.com/conradjones/winstall) to automate installation of components. 

Orchestrates the virtual machine and image creation for building CI images

## Supported Configurations

Currently supported hypervisors :

* Libvirt (QEMU/KVM)
* VMware Fusion

Currently supported guest image operating systems :
* Windows

Currently supported operating systems to run Image Builder from :
* Linux
* MacOS
 

## How it works

Image builder is written in python.

Imagebuilder creates a temporary virtual machine and disk image, with the windows installation media
mounted, starts the virtual machine which boots from the iso and starts the windows installation.

Imagebuilder then waits until it is able to connect to the virtual machine via WinRS to automate the 
installation of software components.

Imagebuilder knows the IP address of the virtual machine to connect via WinRS as, as part of the 
creation process it creates a floppy image which contains an autounattend.xml file to automate 
the installation of windows, and bootstrap.ps1 which sends a http request back to machine running 
image builder containing the IP Address of the guest virtual machine.




