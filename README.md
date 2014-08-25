pyLoadTui
=========

**pyLoadTui** is a text user interface client for pyload using the curses library.  
pyLoad itself comes with a command-line client, pyLoadCli, which may be sufficient for occasional use, but lacks of comfortable user experience and extensive control of pyLoad.
Thus pyLoadTui aims to provide more comfort and functionality, orientating itself to the well-made pyLoad web interface.

Features
--------
- simple and fast user interface
- Display current downloads, queue, collector

Start pyLoadTui
---------------
To start the script, just type the following command in a terminal  
	python pyLoadTui
	
If you start pyLoadTui for the first time, it will ask you for your pyLoad server data, which will be stored in the profiles file in the pyLoadTui directory.
You will be also asked for the password required to connect to the pyLoad server, this will not be saved, thus you will need to type in your password at every start of the script.

Controlling pyLoadTui
---------------------
up / down - scroll  
home / end - prev. / next tab (Downloads / Queue / Collector)

