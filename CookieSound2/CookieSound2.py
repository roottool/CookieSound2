import socket
import string
import re
import os
import glob
import threading
#Read config.ini
import configparser

from pygame import mixer

#open a connection with the server
def irc_conn():
    IRC.connect((SERVER, PORT))

#simple function to send data through the socket
def send_data(command):
    status = IRC.send((command + "\r\n").encode(CHARCODE)) # unicode -> iso2022_jp
    print(command)
    if status == -1 :raise Exception('send_data error', status)

#join the channel
def join(channel):
    send_data("JOIN %s" % channel)

#send login data (customizable)
def login(nickname, username='user', password = None, realname='Marina', hostname='Helena', servername='Server'):
    send_data("USER %s %s %s %s" % (username, hostname, servername, realname))
    send_data("NICK " + nickname)

def wait_connection():
    while(1):
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[3] == ":Welcome" and msg[2] == NICKNAME: #TODO splash screen
            send_data("ze")
            break

def keyhook():
    while(1):
        str = input("Input:")
        if str in OGGlist: 
            send_data(str)
        elif str in list:
            send_data(str)

if __name__ == '__main__':
    #some user data, change as per your taste
    CHARCODE = 'iso2022_jp'
    SERVER = 'irc.ircnet.ne.jp'
    PORT = 6664
    NICKNAME = 'defpo'
    CHANNEL = '#cookie_channel'

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
    
    wait_connection()

    th_me = threading.Thread(target=keyhook)
    th_me.start()

    while (1):
        buffer = IRC.recv(1024)
        msg = str.split(str(buffer))
        if msg[0] == "PING":                #check if server have sent ping command
            send_data("PONG %s" % msg[1])   #answer with pong as per RFC 1459
        if msg[1] == 'PRIVMSG':
            tmp_fname = re.sub(r"^:", "", msg[3])
            filename = re.sub(r"\\r\\n'$", "", tmp_fname)
            if filename in OGGlist: 
                sound = mixer.Sound("sound\\" + filename + ".ogg")
                sound.play()
            elif filename in MP3list:
                mixer.music.load("sound\\csr\\" + filename + ".mp3")
                mixer.music.play()

            #filetxt = open('/tmp/msg.txt', 'a+') #open an arbitrary file to store the messages
            #nick_name = msg[0][:string.find(msg[0],"!")] #if a private message is sent to you catch it
            #message = ' '.join(msg[3:])
            #filetxt.write(string.lstrip(nick_name, ':') + ' -&gt; ' + string.lstrip(message, ':') + '\n') #write to the file
            #filetxt.flush() #don't wait for next message, write it now!