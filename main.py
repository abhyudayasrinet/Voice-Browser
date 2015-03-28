# pulseaudio --kill

# jack_control start

# jack_control exit

# pulseaudio --start


import pyaudio,os
import speech_recognition
from threading import Thread
import subprocess
import webkit
import html2text
import gtk

speechRecognizer = None
openWebpage = None



class Browser():

	def __init__(self):

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
		self.addressBarGoButton.connect('clicked',self.goToAddress)
		self.addressBarLayout.pack_start(self.addressBarGoButton,expand = False, fill = False)
		
		self.addressBarSpeakButton = gtk.Button("Listen")
		self.addressBarSpeakButton.connect('clicked',self.ListenAddress)	
		self.addressBarLayout.pack_start(self.addressBarSpeakButton,expand = False, fill = False)
		
		self.browserWindow = gtk.ScrolledWindow()
		self.mainVerticalLayout.pack_start(self.browserWindow)

		self.browserWebView = webkit.WebView()
		self.browserWindow.add(self.browserWebView)
		self.browserWebView.connect("load-finished", self.getPageContent)

		self.mainWindow.show_all()

		gtk.main()

	def speechListener(self,source):

		global speechRecognizer,openWebpage
		print("listening...")
		# audio = speechRecognizer.listen(source,3)
		audio = speechRecognizer.record(source,3)
		print("done listening!")
		try:
			user = speechRecognizer.recognize(audio)
			print('You said '+user)
			openWebpage = user
			stream = subprocess.Popen(['espeak',str(user)])
			# out,err = stream.communicate()
			# print(out,err)
		except LookupError:
			stream = subprocess.Popen(['espeak','please say that again'])
			print("Can't understand")
		

	def goToURL(self,url):
		if(url == "google"):
			self.browserWebView.open("http://www.google.com")
		elif(url == "facebook"):
			self.browserWebView.open("http://www.facebook.com")
		elif(url == "quora"):
			self.browserWebView.open("http://www.quora.com")
		else:
			self.browserWebView.open(url)

		
	def getPageContent(self,webview, frame):
		stream = subprocess.Popen(['espeak','page loaded'])
		x = self.browserWebView.get_main_frame().get_data_source().get_data()
		print(html2text.html2text(x))


	def goToAddress(self, widget):
		add = self.addressBarText.get_text()
		self.goToURL(add)


	def ListenAddress(self,widget):

		global speechRecognizer,openWebpage
		speechRecognizer = speech_recognition.Recognizer()
		speechRecognizer.energy_threshold = 1000
		speechRecognizer.pause_threshold = 0.5
		with speech_recognition.Microphone() as source:
			listenerThread = Thread(target = self.speechListener, args = (source, ))
			listenerThread.start()
			listenerThread.join()
			print("finished listening")
		
		self.goToURL(openWebpage)


if __name__ == "__main__":	

	browser = Browser()

	

	

	

	




#WORKING
#Recognize from audio file
# import speech_recognition as speech_recognition
# r = speech_recognition.Recognizer()
# with speech_recognition.WavFile("opengoogle.wav") as source:        # use "test.wav" as the audio source
#     audio = r.record(source)                        # extract audio data from the file

# try:
#     list = r.recognize(audio,True)                  # generate a list of possible transcriptions
#     print("Possible transcriptions:")
#     for prediction in list:
#         print(" " + prediction["text"] + " (" + str(prediction["confidence"]*100) + "%)")
# except LookupError:                                 # speech is unintelligible
#     print("Could not understand audio")