from pythonosc import udp_client, osc_server, dispatcher
from time import sleep
import threading
from random import random, randint

"""
The OSC messages are as follows:
/switch
/

"""

def sendOutputGain(gain):
    client.send_message("/output/gain", float(gain))

# def sendReverbGain(gain):
#     client.send_message("/reverb/gain", float(gain))

def sendWetDryGain(gain):
    client.send_message("/wetdry/gain", float(gain))

def sendSwitchEvent(value):
    client.send_message("/switch", int(value))

def sendEncVal(encNum, value):
    client.send_message("/encoder", (encNum, float(value)))

def sendStompEvent(stompNum):
    client.send_message("/stomp", stompNum)

def recvDisplayMsg(msg, t1, t2, t3, t4):
    print(msg, " received display message")
    print(t1)
    print(t2)
    print(t3)
    print(t4)

def recvModeInfo(msg,  modeName):
    print("{} received mode message {}".format(msg, modeName))

def recvEncoderInfo(msg, encNum, name, minv, maxv, step, start):
    print("{} received encoder message {}".format(msg, encNum))
    print("min {} max {}".format(minv, maxv))
    print("step {} start {}".format(step, start))

def recvNeoPixelInfo(msg, pNum, color, bright):
    print(msg, " received neopixel message")
    print("num {} color {} bright {}".format(pNum, color, bright))

def recvSwitchInfo(msg, value):
    print(msg, " received switch message ", value)


ip = "127.0.0.1"# the IP of whatever computer this program is running on
# do not change this, it is required for OSC communication between
# this program and python
send_port = 6449
client = udp_client.SimpleUDPClient(ip, send_port)
print("listening to : {}".format((ip, send_port)))

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/display", recvDisplayMsg)
dispatcher.map("/switchInfo", recvSwitchInfo)
dispatcher.map("/neopixel", recvNeoPixelInfo)
dispatcher.map("/encoderInfo", recvEncoderInfo)
dispatcher.map("/modeInfo", recvModeInfo)
recv_port = 6450
ip = "127.0.0.1"
server = osc_server.ForkingOSCUDPServer(
        (ip, recv_port), dispatcher)
server_thread = threading.Thread(target=server.serve_forever)
print("serving on {}".format(server.server_address))
server_thread.start()

if __name__ == "__main__":
    while (True):
        sendWetDryGain(random())
        sleep(2)
        # sendReverbGain(random())
        # sleep(2)
        sendOutputGain(random())
        sleep(2)
        sendSwitchEvent(randint(0, 4))
        sleep(2)
        sendStompEvent(randint(0,2))
        sleep(2)
        sendEncVal(randint(0,2), random())
        sleep(2)
