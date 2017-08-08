import socket
import string
import re
import os
import time
import glob
import threading
import configparser
import sys
from pygame import mixer
from pyhooked import Hook, KeyboardEvent
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from mainform import Ui_Form

isInput = False
str_input = ''
sound = None


class MainForm(QDialog):
    def __init__(self,parent=None):
        super(MainForm, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.buttonClicked)

    def buttonClicked(self):
        sender = self.sender()
        self.ui.label.setText("puha")
        play(None, 'puha', 0)


#open a connection with the server
def irc_conn():
    IRC.connect((SERVER, PORT))

#send login data (customizable)
def login(nickname, username='user', password = None, realname='Marina', hostname='Helena', servername='Server'):
    send_data('USER %s %s %s %s' % (username, hostname, servername, realname))
    send_data('NICK ' + nickname)

#join the channel
def join(channel):
    send_data('JOIN %s' % channel)

#simple function to send data through the socket
def send_data(command):
    status = IRC.send(bytes((command + '\r\n').encode(CHARCODE))) # unicode -> iso2022_jp
    if status == -1 :raise Exception('send_data error', status)

def send_msg(msg): # sends messages to the target.
    IRC.send(bytes('PRIVMSG '+ CHANNEL +' :'+ msg +'\n', CHARCODE))

def wait_connection(volume):
    while(1):
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[3] == ':Welcome' and msg[2] == NICKNAME: #TODO splash screen
            print('Join ' + CHANNEL)
            play(None, 'haittyatta', 0)
            break

def receive(volume, soundvolume, OGGlist, MP3list):
    while True:
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[0] == "b'PING":                #check if server have sent ping command
            send_data('PONG %s' % msg[1])   #answer with pong as per RFC 1459
        if msg[1] == 'PRIVMSG':
            tmp_sname = re.sub(r"^b':", '', msg[0])
            send_name = tmp_sname.split('!')
            tmp_fname = re.sub(r"^:", '', msg[3])
            filename = re.sub(r"\\r\\n'$", '', tmp_fname)
            play(send_name[0], filename, soundvolume)
                
                
def keyhook(volume, soundvolume, OGGlist, MP3list):
    while True:
        hk = Hook()                 # make a new instance of PyHooked
        hk.handler = handle_events  # add a new shortcut ctrl+a, or triggered on mouseover of (300,400)
        hk.hook()                   # hook into the events, and listen to the presses

def handle_events(args):
    global isInput
    global str_input
    global sound

    if isinstance(args, KeyboardEvent):
        if isInput == True and args.current_key == 'Return' and args.event_type == 'key up':
            isInput = False
            if str_input == 'stop':
                mixer.music.stop()
                sound.stop()
            else:
                play(NICKNAME, str_input, soundvolume)
            str_input = ''
        elif isInput == True and args.current_key == 'Back' and args.event_type == 'key up':
            str_input = str_input[:-1]
        elif isInput == True and (65 <= args.key_code and args.key_code <= 90) and args.event_type == 'key up':
            str_input = str_input + args.current_key.lower()
        elif isInput == True and (48 <= args.key_code and args.key_code <= 57) and args.event_type == 'key up':
            str_input = str_input + args.current_key
        elif isInput == True and (96 <= args.key_code and args.key_code <= 105) and args.event_type == 'key up':
            str_input += args.current_key[-1]
        elif isInput == True and args.current_key == 'Oem_Minus' and args.event_type == 'key up':
            str_input += '-'
        elif isInput == True and args.current_key == 'Oem_7' and args.event_type == 'key up':
            str_input += '^'
  
        if isInput == False and args.current_key == HOOKKEY.upper() and args.event_type == 'key up':
            print('u can input commands')
            isInput = True
            play(None, HOOKSOUND, 0)


def play(name, command, soundvolume):
    global sound

    if command in OGGlist: 
        if name != None:
            print(name + ':' + command)
        if os.path.exists(OGGlist[command]):
            sound = mixer.Sound(OGGlist[command])
            sound.set_volume(volume / 100)
            sound.play()
    elif command in MP3list:
        if name != None:
            print(name + ':' + command)
        if os.path.exists(MP3list[command]):
            mixer.music.load(MP3list[command])
            mixer.music.set_volume(soundvolume / 100)
            mixer.music.play()


if __name__ == '__main__':
    CHARCODE = 'iso2022_jp'
    
    app = QApplication(sys.argv)

    # Create and display the splash screen
    splash_pix = QPixmap('splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    
    config = configparser.RawConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
    else:
        sys.exit()

    SERVER = config.get('Irc_server', 'address')
    PORT = config.getint('Irc_server', 'port')
    CHANNEL = config.get('Irc_server', 'channel')
    NICKNAME = config.get('Irc_server', 'nickname')

    HOOKKEY = config.get('Hook', 'hookkey')
    HOOKSOUND = config.get('Hook', 'hooksound')
    
    isMP3play = config.get('Other', 'bgm')
    volume = config.getfloat('Other', 'volume')
    if isMP3play.capitalize() == 'True':
        soundvolume = config.getfloat('Other', 'volume')
    else:
        soundvolume = 0

    #open a socket to handle the connection
    IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mixer.init()
    irc_conn()
    login(NICKNAME)
    join(CHANNEL)
    
 
    OGGlist = {}
    for tmplist in glob.glob('sound/*.ogg') :
        tmpf, ext = os.path.splitext(tmplist)
        OGGlist[tmpf[6:]] = tmpf + ext
    
    MP3list = {}
    for tmplist in glob.glob('sound/csr/*.mp3') :
        tmpf, ext = os.path.splitext(tmplist)
        MP3list[tmpf[10:]] = tmpf + ext


    wait_connection(volume)

    th_keyhook = threading.Thread(target=keyhook, args=(volume, soundvolume, OGGlist, MP3list))
    th_keyhook.start()

    th_receive = threading.Thread(target=receive, args=(volume, soundvolume, OGGlist, MP3list))
    th_receive.start()

    window = MainForm()
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())