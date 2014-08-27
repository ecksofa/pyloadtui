pyLoadTui
=========

**pyLoadTui** is a text user interface client for pyload using the curses library.  
pyLoad itself comes with a command-line client, pyLoadCli, which may be sufficient for occasional use, but lacks of comfortable user experience and extensive control of pyLoad.
Thus pyLoadTui aims to provide more comfort and functionality, orientating itself to the well-made pyLoad web interface.

Features
--------
- simple and fast user interface
- Display current downloads, queue, collector
- add and remove links / packages
- simply add new links to existing packages
- ... much more to come

Starting pyLoadTui
------------------
To start the script, just type the following command in a terminal  
	python pyLoadTui.py
	
If you start pyLoadTui for the first time, it will ask you for your pyLoad server data, which will be stored in the profiles file in the pyLoadTui directory.
You will be also asked for the password required to connect to the pyLoad server, this will not be saved, thus you will need to type in your password at every start of the script.

Controlling pyLoadTui
---------------------
up / down - scroll  
left / right - prev. / next tab (Downloads / Queue / Collector)  
space bar - expand / collaps package file list  
A - add link to selected package or create new package  
R - remove link / package from pyLoad  
Q - quit

Adding links
------------
You can add links by pressing 'a' or 'A'.
The new links will be submitted to the queue or collector, depending on where you used the shortcut:  
Downloads / Queue -> Queue  
Collector -> Collector  
If you add links while you are at the Queue or Collector tab, you will see that the selected package's name will be proposed as the package name for your new links, indicated by quare brackets "[selected-package-name]".
Thus, if you input an empty line as package name, the new links will be added to the existing package.
