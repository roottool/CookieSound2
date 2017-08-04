import socket
import string
import re
import os
import time
import glob
import threading
#TODO Read config.ini all contents
import configparser

from pygame import mixer
from pyhooked import Hook, KeyboardEvent

import youtube_dl
import pyperclip

str_input = ''
sound = None

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


#open a connection with the server
def irc_conn():
    IRC.connect((SERVER, PORT))

#send login data (customizable)
def login(nickname, username='user', password = None, realname='Marina', hostname='Helena', servername='Server'):
    send_data("USER %s %s %s %s" % (username, hostname, servername, realname))
    send_data("NICK " + nickname)

#join the channel
def join(channel):
    send_data("JOIN %s" % channel)

#simple function to send data through the socket
def send_data(command):
    status = IRC.send(bytes((command + "\r\n").encode(CHARCODE))) # unicode -> iso2022_jp
    if status == -1 :raise Exception('send_data error', status)

def send_msg(msg): # sends messages to the target.
    IRC.send(bytes("PRIVMSG "+ CHANNEL +" :"+ msg +"\n", CHARCODE))

def wait_connection(volume):
    while(1):
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[3] == ":Welcome" and msg[2] == NICKNAME: #TODO splash screen
            print("Join " + CHANNEL)
            if os.path.exists("sound\\haittyatta.ogg"):
                sound = mixer.Sound("sound\\haittyatta.ogg")
                sound.set_volume(volume / 100)
                sound.play()
            break

def receive(volume, OGGlist, MP3list):
    while True:
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[0] == "PING":                #check if server have sent ping command
            send_data("PONG %s" % msg[1])   #answer with pong as per RFC 1459
        if msg[1] == 'PRIVMSG':
            tmp_sname = re.sub(r"^b':", "", msg[0])
            send_name = tmp_sname.split("!")
            tmp_fname = re.sub(r"^:", "", msg[3])
            filename = re.sub(r"\\r\\n'$", "", tmp_fname)
            play(send_name[0], filename)
                
                
def keyhook(NICKNAME, volume, OGGlist, MP3list):
    while True:
        hk = Hook()  # make a new instance of PyHooked
        hk.handler = handle_events  # add a new shortcut ctrl+a, or triggered on mouseover of (300,400)
        hk.hook() # hook into the events, and listen to the presses

def handle_events(args):
    global str_input
    global sound

    if isinstance(args, KeyboardEvent):
        if args.current_key == 'Return' and args.event_type == 'key up':
            if str_input == 'stop':
                mixer.music.stop()
                sound.stop()
            else:
                play(NICKNAME, str_input)
            str_input = ''
        elif args.current_key == 'V' and args.event_type == 'key up' and 'Lcontrol' in args.pressed_key:
            str_input = pyperclip.paste()
        elif args.current_key == 'C' and args.event_type == 'key up' and 'Lcontrol' in args.pressed_key:
            sys,exit()
        elif args.current_key == 'Back' and args.event_type == 'key up':
            str_input = str_input[:-1]
        elif (65 <= args.key_code and args.key_code <= 90) and args.event_type == 'key up':
            str_input = str_input + args.current_key.lower()
        elif (48 <= args.key_code and args.key_code <= 57) and args.event_type == 'key up':
            str_input = str_input + args.current_key
        elif (96 <= args.key_code and args.key_code <= 105) and args.event_type == 'key up':
            str_input += args.current_key[-1]
        elif args.current_key == 'Oem_Minus' and args.event_type == 'key up':
            str_input += '-'
        elif args.current_key == 'Oem_7' and args.event_type == 'key up':
            str_input += '^'


def play(name, command):
    global sound

    if command in OGGlist: 
        print(name + ":" + command)
        if os.path.exists("sound/" + command + ".ogg"):
            sound = mixer.Sound("sound/" + command + ".ogg")
            sound.set_volume(volume / 100)
            sound.play()
    elif command in MP3list:
        print(name + ":" + command)
        if os.path.exists("sound/csr/" + command + ".mp3"):
            mixer.music.load("sound/csr/" + command + ".mp3")
            mixer.music.set_volume(volume / 100)
            mixer.music.play()    
    elif len(command) == 11 :
        print(name + ":" + command)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['http://www.youtube.com/watch?v=' + command])
        path = glob.glob('*.mp3')
        if os.path.exists(path[0]):
            mixer.music.load(path[0])
            mixer.music.set_volume(volume / 100)
            mixer.music.play()


if __name__ == '__main__':
    CHARCODE = 'iso2022_jp'
    
    config = configparser.RawConfigParser()
    if os.path.exists("config.ini"):
        config.read("config.ini")
    else:
        sys.exit()

    SERVER = config.get("Irc_server", "address")
    PORT = config.getint("Irc_server", "port")
    CHANNEL = config.get("Irc_server", "channel")
    NICKNAME = config.get("Irc_server", "nickname")

    #open a socket to handle the connection
    IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mixer.init()
    irc_conn()
    login(NICKNAME)
    join(CHANNEL)
    
    OGGlist = []
    for tmplist in glob.glob("sound/*.ogg") :
        tmpf, ext = os.path.splitext(tmplist)
        OGGlist.append(os.path.basename(tmpf))

    MP3list = []
    for tmplist in glob.glob("sound/csr/*.mp3") :
        tmpf, ext = os.path.splitext(tmplist)
        MP3list.append(os.path.basename(tmpf))

    OGGlist.sort()
    MP3list.sort()
    
    volume = config.getfloat("Other", "volume")

    wait_connection(volume)

    th_keyhook = threading.Thread(target=keyhook, args=(NICKNAME, volume, OGGlist, MP3list))
    th_keyhook.start()

    receive(volume, OGGlist, MP3list)