# pulseaudio --kill

# jack_control start

# jack_control exit

# pulseaudio --start


import pyaudio,os
import speech_recognition
from threading import Thread
from pygoogle import pygoogle
import time
import subprocess
import webkit
import html2text
import gtk

speechRecognizer = None



class Browser():

    def __init__(self):

        self.command = ''#'search pizza'
        self.linkDict = {}
        self.history = ['']
        self.historyIndex = 0
        self.bookmarks = []
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
        if(text.startswith('http://') or text.startswith('https://') ):
            self.goToURL(text)
        else:
            text = 'https://'+text
            self.addressBarText.set_text(text)
            self.goToURL(text)


    def speechListener(self,source):

        global speechRecognizer,openWebpage
        print("listening...")
        # audio = speechRecognizer.listen(source,3)
        audio = speechRecognizer.record(source,3)
        print("done listening!")
        try:
            self.command = speechRecognizer.recognize(audio)
            print('You said '+self.command)
            stream = subprocess.Popen(['espeak',str(self.command)])
            stream.wait()
            # out,err = stream.communicate()
            # print(out,err)
        except LookupError:
            stream = subprocess.Popen(['espeak','please say that again'])
            self.command = ''
            print("Can't understand")

        
    def listenerThread(self,widget):

        global speechRecognizer
        speechRecognizer = speech_recognition.Recognizer()
        speechRecognizer.energy_threshold = 2000
        speechRecognizer.pause_threshold = 0.5
        with speech_recognition.Microphone() as source:
            listenerThread = Thread(target = self.speechListener, args = (source, ))
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
                self.goToURL(self.linkDict[self.getNumber(words[2])])
            else:
                self.goToURL(words[1])

        elif(words[0] == "search"):
            self.searchGoogle(words[1:])

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
            print("linkDict:",self.linkDict)

        elif(self.command == "read page content"):
            self.getPageContent()


    def goToURL(self, url, fowback = False):

        print("opening url:",url)
        if(url == "google"):
            self.browserWebView.open("http://www.google.com")
        elif(url == "facebook"):
            self.browserWebView.open("http://www.facebook.com")
        elif(url == "quora"):
            self.browserWebView.open("http://www.quora.com")
        else:
            self.browserWebView.open(url)

        if(not fowback):
            del self.history[self.historyIndex+1:]
            self.history.append(url)
            self.historyIndex = len(self.history) - 1

    
    def searchGoogle(self, query):

        query = ' '.join(query)
        g = pygoogle(query,1)
        searchDict = g.search()
        i = 1
        for key in searchDict:
            print(key,":",str(searchDict[key]))
            #uncomment to speak out links in order
            # stream = subprocess.Popen(['espeak','Link '+str(i)])
            # stream.wait()
            # stream = subprocess.Popen(['espeak',str(key).encode('utf-8')])
            # stream.wait()
            self.linkDict[i] = searchDict[key]
            i += 1
        print("linkdict:",self.linkDict)


    def getNumber(self, word):
        print("getNumber : ",word)
        if(type(word) == int):
            return word
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

    def pageLoaded(self,webview, frame):
        stream = subprocess.Popen(['espeak','page loaded'])

    def getPageContent(self):
        x = self.browserWebView.get_main_frame().get_data_source().get_data()
        h = html2text.HTML2Text()
        h.ignore_links = True
        # print(html2text.html2text(x))
        print(h.handle(x))


    

    


if __name__ == "__main__":  

    browser = Browser()
    