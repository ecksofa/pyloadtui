"""
 This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

 author: ecksofa
"""

import os
import sys
import time
import curses
from module.remote.thriftbackend.ThriftClient import  ThriftClient, WrongLogin
from getpass import getpass

path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"

fileProfiles = path + "profiles"

username = ""
password = ""
host = ""
port = 0

reloadTime = 2
downloadStatus = ["Finished", "Offline", "Online", "Queued", "Skipped", "Waiting", "TempOffline", "Starting", "Failed", "Aborted", "Decrypting", "Custom", "Downloading", "Processing", "Unknown"]

class Tabs:
	def __init__(self, window):
		self.window = window
		self.selected = 0
#		self.entries = ["Downloads", "Queue", "Collector", "pyLoad", "TUI"]
		self.entries = ["Downloads", "Queue", "Collector"]
	
	def draw(self):
		self.window.erase()
		
		self.window.move(0,0)
		for i,e in enumerate(self.entries):
			self.window.addstr(" ")
			if i == self.selected:
				self.window.addstr(e, curses.A_REVERSE)	
			else:
				self.window.addstr(e)	
			
		self.window.refresh()
	
	def move(self, d):
		self.selected += d
		if self.selected < 0:
			self.selected = 0
		if self.selected > len(self.entries)-1:
			self.selected = len(self.entries)-1
		
		self.draw()
		return self.selected
		

class Downloads:	
	def __init__(self, window):
		self.window = window
		self.load()
		self.scrollOffset = 0
	
	def load(self):
		self.entries = client.statusDownloads()
		
		self.lines = []
		for e in self.entries:
			tmp =  ("  " + e.name)
			self.lines.append(tmp)
			tmp = ("   " + downloadStatus[e.status])
			tmp += ("  " + e.format_eta + " @ " + ("%.2f" % (e.speed / 1024.)) + " KiB/s")
	#		tmp += ("\t" + e.format_size)
	#		tmp += ("\t" + str(e.percent) + "% / " + ("%.2f" % ((e.size-e.bleft) / (1024*1024.))) + " MiB")
			tmp += ("  " + ( "%.2f MiB / %.2f MiB" % ((e.size-e.bleft) / (1024*1024.), e.size / (1024*1024.)) ) )
			self.lines.append(tmp)
			barwidth = width - 14
			tmp = ("   [" + "#"*int(e.percent/100.*barwidth) + " "*int(barwidth - e.percent/100.*barwidth) + "]")
			self.lines.append(tmp)
	
	def handleKey(self, key):
		pass
	
	def scroll(self, scr):
		if scr < 0:
			if self.scrollOffset + scr > 0:
				self.scrollOffset += scr
			else:
				self.scrollOffset = 0
		elif scr > 0:
			if self.scrollOffset + scr < len(self.lines) - (self.window.getmaxyx()[0]-2):
				self.scrollOffset += scr
			else:
				self.scrollOffset = len(self.lines) - (self.window.getmaxyx()[0]-2)
	
	def draw(self):
		self.window.erase()
		
		self.window.move(1,0)
		for l in self.lines[self.scrollOffset : self.scrollOffset+self.window.getmaxyx()[0]-2]:
			self.window.addstr(l + "\n")	
			
		self.window.border()
		self.window.refresh()
	
	def getDestination(self):
		return 1
	
	def getPropPackName(self):
		return ""

class Queue:	
	def __init__(self, window):
		self.window = window
		self.scrollOffset = 0
		self.selected = 0
		self.expanded = []
		
		self.load()
			
	def load(self):
		self.entries = client.getQueueData()
		
		self.items = []
		for e in self.entries:
			self.items.append([])
			tmp =  (e.name)
			self.items[-1].append(tmp)
			self.items[-1].append(e.pid in self.expanded)
			self.items[-1].append([])
			for l in e.links:
				tmp = l.name
				tmp += " (" + downloadStatus[l.status] + ")"
				self.items[-1][2].append([tmp, l.fid])
			self.items[-1].append(e.pid)
		self.prepareLines()
		self.scroll(0)
		
	def handleKey(self, key):
		if  self.selected < 0:
			return False
			
		if key == ord(' '):
			if self.lines[self.selected][2] == -1:
				item = self.items[self.lines[self.selected][1]]
				if item[1]:
					self.expanded.remove(item[3])
				else:
					self.expanded.append(item[3])
				item[1] = not item[1]
				self.prepareLines()
				self.draw()
		elif key == ord('r') or key == ord('R'):
			target = self.lines[self.selected]
			if target[2] == -1:
				client.deletePackages([ self.items[target[1]][3] ])
			else:
				client.deleteFiles([ self.items[target[1]][2][target[2]][1] ])
			self.load()
			self.draw()
		elif key == ord('m') or key == ord('M'):
			target = self.lines[self.selected]
			if target[2] == -1:
				client.movePackage(0, self.items[target[1]][3])
			self.load()
			self.draw()
	
	def scroll(self, scr):
		self.selected += scr
		if self.selected < 0:
			self.selected = 0
		elif self.selected > len(self.lines) - 1:
			self.selected = len(self.lines) - 1
		if self.scrollOffset > self.selected:
			self.scrollOffset = self.selected
		elif self.scrollOffset < self.selected - (self.window.getmaxyx()[0]-2) + 1:
			self.scrollOffset = self.selected - (self.window.getmaxyx()[0]-2) + 1
				
	def prepareLines(self):
		self.lines = []
		for k, i in enumerate(self.items):
			self.lines.append([])
			self.lines[-1].append("  " + i[0])
			self.lines[-1].append(k)
			self.lines[-1].append(-1)
			if i[1]:
				for l, j in enumerate(i[2]):
					self.lines.append([])
					self.lines[-1].append("   " + j[0])
					self.lines[-1].append(k)
					self.lines[-1].append(l)
	
	def draw(self):
		global log
		self.window.erase()
		
		self.window.move(1,0)
		
		lCount = 0
		for i, l in enumerate(self.lines[self.scrollOffset : self.scrollOffset+self.window.getmaxyx()[0]-2]):
			attr = curses.A_NORMAL
			if i + self.scrollOffset == self.selected:
				attr = attr | curses.A_REVERSE
			if l[2] == -1:
				attr = attr | curses.color_pair(1)
			if l[0][-8:] == "(Failed)" or l[0][-9:] == "(Offline)":
				attr = attr | curses.color_pair(2)
				
			self.window.addstr(l[0] + "\n", attr)	
			
		self.window.border()
		self.window.refresh()
	
	def getDestination(self):
		return 1
	
	def getPropPackName(self):
		if self.selected < 0:
			return ""
		else:
			return self.items[self.lines[self.selected][1]][0]

class Collector:	
	def __init__(self, window):
		self.window = window
		self.scrollOffset = 0
		self.selected = 0
		self.expanded = []
		
		self.load()
	
	def load(self):
		self.entries = client.getCollectorData()
		
		self.items = []
		for e in self.entries:
			self.items.append([])
			tmp =  (e.name)
			self.items[-1].append(tmp)
			self.items[-1].append(e.pid in self.expanded)
			self.items[-1].append([])
			for l in e.links:
				tmp = l.name
				tmp += " (" + downloadStatus[l.status] + ")"
				self.items[-1][2].append([tmp, l.fid])
			self.items[-1].append(e.pid)
		self.prepareLines()
		self.scroll(0)
	
	def handleKey(self, key):
		if  self.selected < 0:
			return False
		
		if key == ord(' '):
			if self.lines[self.selected][2] == -1:
				item = self.items[self.lines[self.selected][1]]
				if item[1]:
					self.expanded.remove(item[3])
				else:
					self.expanded.append(item[3])
				item[1] = not item[1]
				self.prepareLines()
				self.draw()
		elif key == ord('r') or key == ord('R'):
			target = self.lines[self.selected]
			if target[2] == -1:
				client.deletePackages([ self.items[target[1]][3] ])
			else:
				client.deleteFiles([ self.items[target[1]][2][target[2]][1] ])
			self.load()
			self.draw()
		elif key == ord('m') or key == ord('M'):
			target = self.lines[self.selected]
			if target[2] == -1:
				client.movePackage(1, self.items[target[1]][3])
			self.load()
			self.draw()
	
	def scroll(self, scr):
		self.selected += scr
		if self.selected < 0:
			self.selected = 0
		elif self.selected > len(self.lines) - 1:
			self.selected = len(self.lines) - 1
		if self.scrollOffset > self.selected:
			self.scrollOffset = self.selected
		elif self.scrollOffset < self.selected - (self.window.getmaxyx()[0]-2) + 1:
			self.scrollOffset = self.selected - (self.window.getmaxyx()[0]-2) + 1
		if self.scrollOffset < 0:
			self.scrollOffset = 0
				
	def prepareLines(self):
		self.lines = []
		for k, i in enumerate(self.items):
			self.lines.append([])
			self.lines[-1].append("  " + i[0])
			self.lines[-1].append(k)
			self.lines[-1].append(-1)
			if i[1]:
				for l, j in enumerate(i[2]):
					self.lines.append([])
					self.lines[-1].append("    " + j[0])
					self.lines[-1].append(k)
					self.lines[-1].append(l)
	
	def draw(self):
		self.window.erase()
		
		self.window.move(1,0)
		
		lCount = 0
		for i, l in enumerate(self.lines[self.scrollOffset : self.scrollOffset+self.window.getmaxyx()[0]-2]):
			attr = curses.A_NORMAL
			if i + self.scrollOffset == self.selected:
				attr = attr | curses.A_REVERSE
			if l[2] == -1:
				attr = attr | curses.color_pair(1)
			if l[0][-8:] == "(Failed)" or l[0][-9:] == "(Offline)":
				attr = attr | curses.color_pair(2)
				
			self.window.addstr(l[0] + "\n", attr)	
			
		self.window.border()
		self.window.refresh()
	
	def getDestination(self):
		return 0
	
	def getPropPackName(self):
		if self.selected < 0:
			return ""
		else:
			return self.items[self.lines[self.selected][1]][0]

def drawFooter():
		winFooter = curses.newwin(1, width, height-1, 0)
		winFooter.addch(" ")
		winFooter.addch("A", curses.color_pair(1) | curses.A_BOLD)
		winFooter.addstr("dd  ")
		winFooter.addch("R", curses.color_pair(1) | curses.A_BOLD)
		winFooter.addstr("emove  ")
		winFooter.addch("M", curses.color_pair(1) | curses.A_BOLD)
		winFooter.addstr("ove  ")
		winFooter.addch("Q", curses.color_pair(1) | curses.A_BOLD)
		winFooter.addstr("uit  ")
		winFooter.refresh()

def loadDefaultProfile():
	global fileProfiles
	global username, host, port
	
	profiles = []
	
	if not os.path.isfile(fileProfiles):
		open(fileProfiles, 'a').close()
	
	fProfiles = open(fileProfiles, 'r')
	for l in fProfiles:
		if '#' in l:
			l = l[:l.find('#')]
		l_split = l.split()
		if len(l_split) != 4:
			continue
		profiles.append([l_split[0], l_split[1], l_split[2], int(l_split[3])])
	fProfiles.close()
	
	if(len(profiles) == 0):
		profiles.append(["default"])
		print "Please create a profile containing information about your pyLoad server.\a"
		print "These informations will be saved to the profiles file in the script's directory."
		print "Only user name, host address and port will be saved, NOT your password."
		profiles[0].append( raw_input('user name: ') )
		profiles[0].append( raw_input('host address: ') )
		profiles[0].append( int(raw_input('host port: ')) )
		
		fProfiles = open(fileProfiles, 'a')
		fProfiles.write("\n" + profiles[0][0] + "\t" + profiles[0][1] + "\t" + profiles[0][2] + "\t" + str(profiles[0][3]))
		fProfiles.close()
		
		
	username = profiles[0][1]
	host = profiles[0][2]
	port = profiles[0][3]

def initClient():
	try:
		global client
		client = ThriftClient(host, port, username, password)
	except:
		print "Login failed: " + username + "@" + host + ":" + str(port)
		exit()

def addLink(destination, propPackName):
	curses.echo(); curses.curs_set(1)
	winLinks = curses.newwin(height, width, 0, 0)
	
	while(True):
		winLinks.erase()
		winLinks.addstr(0, 0, "Enter package name")
		if not propPackName == "":
			 winLinks.addstr("[" + propPackName + "]")
		winLinks.addstr(":\n")
		
		name = winLinks.getstr()
		if name == "":
			name = propPackName
		
		if not name == "":
			break
	
	links = []
	while(True):
		winLinks.erase()
		winLinks.addstr(0, 0, str(len(links)), curses.color_pair(1) | curses.A_BOLD)
		winLinks.addstr(" links collected\nInput new links or an empty line to finish:\n")
		l = winLinks.getstr()
		if l == "":
			break
		else:
			links.append(l)
	
	if destination == 0:
		packs = client.getCollector()
	else:
		packs = client.getQueue()
	
	pid = -1
	for p in packs:
		if name == p.name:
			pid = p.pid
			break
	
	if pid == -1:
		client.addPackage(name, links, destination)
	else:
		client.addFiles(pid, links)
	
	curses.noecho(); curses.curs_set(0)
	

def main(stdscr):
	global reloadTime
	
	curses.noecho(); curses.cbreak(); curses.curs_set(0); stdscr.keypad(1)
	(h,w) = stdscr.getmaxyx()
	global height
	height = h
	global width
	width = w
	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	stdscr.refresh()
	
	winTabs = curses.newwin(1, width, 0, 0)
	winDownloads = curses.newwin(height-2, width, 1, 0)
	winQueue = curses.newwin(height-2, width, 1, 0)
	winCollector = curses.newwin(height-2, width, 1, 0)
	
	wTabs = Tabs(winTabs)
	wDownloads = Downloads(winDownloads)
	wQueue = Queue(winQueue)
	wCollector = Collector(winCollector)
	wArray = [wDownloads, wQueue, wCollector]
	
	wCurrent = wArray[0]
	
	wTabs.draw()
	drawFooter()
	
	stdscr.timeout(reloadTime * 1000)
	last_time = time.time() - reloadTime
	while True:
		if round(time.time() - last_time) >= reloadTime:
			last_time = time.time()
			wCurrent.load()
			
		wCurrent.draw()
		
		key = stdscr.getch()

		if key == curses.KEY_LEFT:
			wCurrent = wArray[wTabs.move(-1)]
			last_time = time.time() - reloadTime
		elif key == curses.KEY_RIGHT:
			wCurrent = wArray[wTabs.move(1)]
			last_time = time.time() - reloadTime
		elif key == curses.KEY_UP:
			wCurrent.scroll(-1)
		elif key == curses.KEY_DOWN:
			wCurrent.scroll(1)   
		elif key == ord('a') or key == ord('A'):
			propPackName = "new Package"
			addLink(wCurrent.getDestination(), wCurrent.getPropPackName())
			
			wTabs.draw()
			drawFooter()
			last_time = time.time() - reloadTime
		elif key == ord('q') or key == ord('Q'):
			break
		else:
			wCurrent.handleKey(key)
	
	curses.echo(); curses.nocbreak(); stdscr.keypad(0)
	curses.endwin()

loadDefaultProfile()
password = getpass("password: ")
initClient()
curses.wrapper(main)
