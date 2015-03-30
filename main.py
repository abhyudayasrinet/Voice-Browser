# pulseaudio --kill

# jack_control start

# jack_control exit

# pulseaudio --start


import pyaudio,os
import speech_recognition
# from threading import Thread
from pygoogle import pygoogle
import gobject
import time
import subprocess
import webkit
import string
import html2text
import threading
import gtk
import urllib2
import bs4

speechRecognizer = None



class Browser():

	def __init__(self):

		self.command = ''#'search pizza'
		self.linkDict = {}
		self.history = ['']
		self.historyIndex = 0
		self.bookmarks = []
		self.audioOutput = True
		# self.recognizeCommand()
		self.init()


	def init(self):

		self.mainWindow = gtk.Window()
		self.mainWindow.set_title("Grizlly Browser")
		# self.mainWindow.set_opacity(0.8)
		self.mainWindow.set_position(gtk.WIN_POS_CENTER)
		self.mainWindow.set_default_size(500,500)
		# self.mainWindow.maximize()
		self.mainWindow.connect('destroy' , lambda w: gtk.main_quit())


		self.mainVerticalLayout = gtk.VBox()
		self.mainWindow.add(self.mainVerticalLayout)

		self.addressBarLayout = gtk.HBox()
		self.mainVerticalLayout.pack_start(self.addressBarLayout,expand = False, fill = False)

		self.addressBarText = gtk.Entry()
		self.addressBarLayout.pack_start(self.addressBarText)

		self.addressBarGoButton = gtk.Button("Go")
		self.addressBarGoButton.connect('clicked',self.goButtonCB)
		self.addressBarLayout.pack_start(self.addressBarGoButton,expand = False, fill = False)

		self.addressBarSpeakButton = gtk.Button("Speak")
		self.addressBarSpeakButton.connect('clicked',self.listenerThread)    
		self.addressBarLayout.pack_start(self.addressBarSpeakButton,expand = False, fill = False)

		self.browserWindow = gtk.ScrolledWindow()
		self.mainVerticalLayout.pack_start(self.browserWindow)

		self.browserWebView = webkit.WebView()
		self.browserWindow.add(self.browserWebView)
		self.browserWebView.connect("load-finished", self.pageLoaded)

		self.mainWindow.show_all()

		gtk.main()


	def goButtonCB(self, widget):
		text = self.addressBarText.get_text()
		text = self.fixURL(text)
		self.goToURL(text)


	def speechListener(self,source):

		global speechRecognizer,openWebpage
		print("listening...")
		# audio = speechRecognizer.listen(source,3)
		audio = speechRecognizer.record(source,4)
		print("done listening!")
		try:
			self.command = speechRecognizer.recognize(audio)
			print('You said '+self.command)
			stream = subprocess.Popen(['espeak',str(self.command)])
			stream.wait()
		except LookupError:
			stream = subprocess.Popen(['espeak','please say that again'])
			self.command = ''
			print("Can't understand")
		self.audioOutput = True

	def listenerThread(self,widget):

		global speechRecognizer
		speechRecognizer = speech_recognition.Recognizer()
		speechRecognizer.energy_threshold = 2000
		speechRecognizer.pause_threshold = 0.5
		with speech_recognition.Microphone() as source:
			self.audioOutput = False
			listenerThread = threading.Thread(target = self.speechListener, args = (source, ))
			listenerThread.start()
			listenerThread.join()
			
			print("finished listening")
		self.recognizeCommand()


	def recognizeCommand(self):
		self.command = self.command.encode('ascii')
		words = self.command.split() #split by spaces
		print(words)


		if(words[0] == "open"):
			if(words[1] == "link"):
				linktag = ' '.join(words[2:])
				link = self.linkDict[self.getLinkTag(linktag)]
				self.goToURL(self.fixURL(link))
			else:
				self.goToURL(words[1])


		elif(words[0] == "search"):
			self.searchGoogle(words[1:])


		elif(self.command == "get hyperlinks" or self.command == "get hyperlink" or self.command == "get hyper links" or self.command == "get hyper link"):
			self.readHyperlinks()

		#todo option to add tag for bookmark
		elif(self.command == "bookmark page"):
			if(self.history[self.historyIndex] not in self.bookmarks):
				self.bookmarks.append(self.history[self.historyIndex])
				stream = subprocess.Popen(['espeak','bookmark added'])
				stream.wait()


		elif(self.command == "go back"):
			self.historyIndex -= 1
			self.goToURL(self.history[self.historyIndex], True)


		elif(self.command == "go forward"):
			self.historyIndex += 1
			self.goToURL(self.history[self.historyIndex], True)            


		elif(self.command == "read bookmarks"):
			self.linkDict = {}       
			i = 1   
			for bookmark in self.bookmarks:
				stream = subprocess.Popen(['espeak','Link '+str(i)])
				stream.wait()
				stream = subprocess.Popen(['espeak',str(bookmark)])
				stream.wait()
				self.linkDict[i] = bookmark
				if(not self.audioOutput):
					return
			print("linkDict:",self.linkDict)


		elif(self.command == "read page content"):
			self.readPageContentThread()


	def fixURL(self, url):

		#if url directs to page in same website
		if(url[0] == '/'):
			url = self.history[self.historyIndex] + url

		#if url doesn't have http:// or https:// as prefix else add it
		if(url.startswith('http://') or url.startswith('https://') ):
			pass
		else:
			url = 'https://'+url
			self.addressBarText.set_text(url)

		if('.com' in url or '.org' in url or '.ac.in' in url):
			pass
		else:
			url = url + '.com'
			self.addressBarText.set_text(url)

		return url


	def goToURL(self, url, fowback = False):
		print("opening url:",url)
		url = self.fixURL(url)
		self.browserWebView.open(url)
		if(not fowback):
			del self.history[self.historyIndex+1:]
			self.history.append(url)
			self.historyIndex = len(self.history) - 1


	def readHyperlinks(self):
		threading.Thread(target = self.readHyperlinksThread, args = () ).start()


	def readHyperlinksThread(self):
		for key in self.linkDict:
			stream = subprocess.Popen(['espeak',str(key)])
			stream.wait()
			if(not self.audioOutput):
				return


	def searchGoogle(self, query):
		self.goToURL('http://www.google.com/search?q='+'+'.join(query))
		threading.Thread(target = self.searchResultThread, args=(query,) ).start()


	def searchResultThread(self, query):
		query = ' '.join(query)
		g = pygoogle(query,1)
		searchDict = g.search()
		i = 1
		for key in searchDict:
			print(key,":",str(searchDict[key]))
			#uncomment to speak out links in order
			stream = subprocess.Popen(['espeak','Link '+str(i)])
			stream.wait()
			stream = subprocess.Popen(['espeak',str(key).encode('utf-8')])
			stream.wait()
			self.linkDict[i] = searchDict[key]
			i += 1
			if(not self.audioOutput):
				return

		print("linkdict:",self.linkDict)


	def getLinkTag(self, word):
		word = word.strip()
		print("getLinkTag : ",word)

		try:
			x = int(word)
			return x
		except:
			pass
		if(word == "zero"):
			return 0
		if(word == "one"):
			return 1
		if(word == "two"):
			return 2
		if(word == "three"):
			return 3
		if(word == "four"):
			return 4
		if(word == "five"):
			return 5
		if(word == "six"):
			return 6
		if(word == "seven"):
			return 7
		if(word == "eight"):
			return 8
		if(word == "nine"):
			return 9
		if(word == "ten"):
			return 10
		return word

	def pageLoaded(self,webview, frame):
		stream = subprocess.Popen(['espeak','page loaded'])
		stream.wait()


	def readPageContentThread(self):
		threading.Thread(target = self.readPageContent, args=() ).start()
		# self.cb()

	def readPageContent(self):
		# METHOD 1
		global website
		x = self.browserWebView.get_main_frame().get_data_source().get_data()
		h = html2text.HTML2Text()
		h.ignore_links = False
		text = str(h.handle(x))
		content = text.split('\n')
		# print(len(content))
		i = 0
		while( i < len(content)):
			content[i] = content[i].strip()	
			if(content[i] == ''):
				i+=1
				continue

			while(content[i][0] == '#'):
				content[i] = content[i][1:]

			if(content[i].startswith('![')): 										# html2text shows image links in the form ![<tag>](link)
				while(content[i].find(']') == -1):									# find closing tag					
					content[i] = content[i] + content[i+1]							# if closing tag not available append next element and search again
					del content[i+1]
				while(content[i].find(')') == -1):									# if link continues to next link append next element and search again
					content[i] = content[i] + content[i+1]
					del content[i+1]
				start = content[i].find('[')										
				end = content[i].find(']')
				content[i] = "Image on "+content[i][start+1:end]					# output audio as "image on <image tag>"

			if(content[i].find('[') >= 0):

				while(True):
					print("hyperlink:",content[i])
					start = content[i].find('[') #hyperlinks are of the from [<tag>](<link>)
					link = '' #to store the hyperlink

					#while hyperlinks might be available
					while(start >= 0):
						end = content[i].find(']',start) #find end bracket
						while(end == -1): 											# if end bracket is not found (the line is extended to the content element)
							content[i] = content[i] + content[i+1]  				# add the next element to the current one
							del content[i+1] 										# delete the next element
							end = content[i].find(']',start)						# find the end bracket again
						if(end+1 < len(content[i]) and content[i][end+1] == '('):   # if the ']'(closing bracket) is followed by a '(' (open parenthesis bracket) then it is a hyperlink
																					# otherwise it's a part of the page content
							start_ = end+1 											# set the start index of the '(' bracket
							end_ = content[i].find(')',start_)						# find the index of the closing ')' bracket
							while(end_ == -1):										# append the next line if the closing bracket is not found in current elment
								content[i] = content[i] + content[i+1]				# append the next element
								del content[i+1]									# delete the next element
								end_ = content[i].find(')',start_)					# find closing ')' again
							link = content[i][start_+1:end_]						# extract the link
							
							content[i] = content[i][0:start_]+content[i][end_+1:]	#delete the (<link>) from the text

						start = content[i].find('[')								# find the open '[' tag
						end = content[i].find(']')									# and the closing ']' tag
						linktag = self.getLinkTag(content[i][start+1:end])
						print("link tag,link ",linktag,":",link)				

						linktag = str(linktag).lower()
						self.linkDict[linktag] = link								# extract the link tag

						start = content[i].find('[')	
						content[i] = content[i][0:start]+content[i][start+1:]
						end = content[i].find(']')
						content[i] = content[i][0:end]+content[i][end+1:]

						start = content[i].find('[')
					else:
						break

			print(content[i])

			stream = subprocess.Popen(['espeak',content[i]])
			stream.wait()

			if(not self.audioOutput):
				return
			# time.sleep(3)
			i+=1

        	

if __name__ == "__main__":  
	gtk.gdk.threads_init()
	browser = Browser()
    