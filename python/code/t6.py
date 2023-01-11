#!/usr/bin/python

import atexit
from collections import defaultdict
import random
import sys
import time
import board
import busio


# Import MPR121 module.
import adafruit_mpr121

import argparse
from pythonosc import udp_client

from lib.mymidi import mymidi, midievent, all_midi_off

# Setup the parser
parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="127.0.0.1",
parser.add_argument("--ip", default="192.168.0.193",
    help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=10111,
    help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)

class CapT(object):
    def __init__(self, num_pads=12):
                # Create I2C bus.
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Create MPR121 object.
        self.cap = adafruit_mpr121.MPR121(self.i2c, address=0x5a)
        
        self.num_pads = num_pads
        self.touched = [] * self.num_pads
        # self.connect()
        print("connected")

    def get_in_touch(self):
        while True:
            try:
                touches = self.cap.touched()
                self.touched = [True and (touches & 1 << i) for i in range(self.num_pads)]
                return self.touched
            except:
                print("connect")
                # self.connect()



def all_osc_off():
  print("all osc off")
  client.send_message("/all_off",1)

  

# atexit.register(all_midi_off,client)
atexit.register(all_osc_off)

# base tempo
TICKS_PER_SEC = 10000.0
# TICKS_PER_SEC = 1000.0
#TICKS_PER_SEC = 500.0
# TICKS_PER_SEC = 225.0
# TICKS_PER_SEC = 100.0

mm = mymidi()
midievent.set_midiout(mm)


# def load_nos(path="/home/pi/SOLACE1.MID.nos"):
# def load_nos(path="../data/SOLACE1_FLORA_SLOW.MID.NOS"):
def load_nos(path="../data/gbert_bergen_022023_1.mid.nos"):
    print( "Opening:", path)

    notes = []
    with open(path) as mfh:
        for line in mfh:
            ticks, note, velocity = [int(x) for x in line.split(", ")]
            notes.append(midievent(0x90, note, velocity, ticks))
            # notes.append([ticks, note, velocity])

    return notes

try:
    notes = load_nos(sys.argv[1])
except:
    notes = load_nos()

total_ticks = sum([note.ticks for note in notes])
print ("Midi file total ticks:", total_ticks)


class SensorParam(object):
    def __init__(self, knob, minval, maxval, duration, increasing=True, whole_num=False):
        self.knob = knob
        self.minval = minval
        self.maxval = maxval
        self.duration = duration

        self.time_per_change = duration / float(maxval - minval)

        self.curval = minval if increasing else maxval

        self.on_ramp = 1 if increasing else -1

        self.last_time = time.time()
        self.whole_num = whole_num
        # print (self.time_per_change)

    def reset_to_min(self):
        # print("reset before", self.curval)
        self.curval = self.minval
        # print("reset after", self.curval)


    def get_out(self, on=False):
        iv = on
        now = time.time()
        delta = now - self.last_time

        on = 1 if on else -1

        val_change = (delta / self.time_per_change) * on * self.on_ramp

        self.curval += val_change
        # if iv: t(self.curval, self.minval,self.maxval)
        self.curval = max(self.curval, self.minval)
        self.curval = min(self.curval, self.maxval)
        self.last_time = now # won't hurt to repeat this

        # if iv:
        #   print ("KNOB, inval, outval, valch:", self.knob, iv, self.curval, val_change)

        if self.whole_num == False:
          return self.knob, self.curval, iv, self.minval
        else:
          return self.knob, int(self.curval), iv, self.minval
        # return self.knob, int(self.curval), iv


# VCO1_PITCH = 2
# VCO2_PITCH = 3
# VCO1_SHAPE = 4
# VCO2_SHAPE = 5
# VOL1_KNOB = 7
# VOL2_KNOB = 8
# CROSS_MOD = 9
# NOISE = 1
# FILTER = 11
# RES = 12
# EG_INT = 13

# SYNC = 80
# RING = 81

# LFO_INT = 26

TEMPO = 100
# min_tps = 250.0
# max_tps = 1000.0

# create a mapping for cap touch pins to midi cc messages
caps = defaultdict(list)
caps = [[] for _ in range(12)]

# note: the call to SensorParam sends the following data:
#   param 1: cc number (referenced in the code as KNOB)
#   param 2: starting midi value (can be 0-127) when cap touch pin is touched
#   param 3: maximum midi value (can be 0-127) that can be reached when touching cap touch pin
#   param 4: note sure what this is...maybe length of time to get to max midi value?
#   param 5: maybe something like: if true ramp value from min to max. if false jump to max value
caps[0].append(SensorParam(0, 0, 10, 3, increasing=True, whole_num=True))
caps[1].append(SensorParam(1, 0, 20, 250, increasing=True))
caps[2].append(SensorParam(2, 0, 127, 250, increasing=True))
caps[3].append(SensorParam(3, 0, 127, 250, increasing=True))
caps[4].append(SensorParam(4, 1, 2, 3, increasing=True, whole_num=True))
caps[5].append(SensorParam(5, 0.5, 1, 1, increasing=True))
caps[5].append(SensorParam(6, 0.5, 0, 10, increasing=True))
caps[7].append(SensorParam(7, 0, 127, 250, increasing=True))
caps[8].append(SensorParam(8, 1, 127, 250, increasing=True))
caps[9].append(SensorParam(9, 1, 4, 2, increasing=True, whole_num=True))
caps[10].append(SensorParam(10, 0, 127, 250, increasing=True))
caps[11].append(SensorParam(11, 0, 127, 250, increasing=True))

# knobs_to_osc = defaultdict(list)
# IMPORTANT: set range in the first line below to the number of knobs you are defining 
knobs_to_osc = [[] for _ in range(12)]
knobs_to_osc[0] = (0,'/oct')
knobs_to_osc[1] = (1,'/glide')
knobs_to_osc[2] = (2,'/wgl')
knobs_to_osc[3] = (3,'/time')
knobs_to_osc[4] = (4,'/buf 1')
knobs_to_osc[5] = (5,'/f 1')
knobs_to_osc[6] = (6,'/rate')
knobs_to_osc[7] = (7,'/pms')
knobs_to_osc[8] = (8,'/ratios')
knobs_to_osc[9] = (9,'/oct 1')
knobs_to_osc[10] = (10,'/drive')
knobs_to_osc[11] = (11,'/crackle')

def find_osc_path_by_knob(kn):
  for knob, path in knobs_to_osc:
    if len(path)>0 and knob == kn:
        # print(knob,path)
        return path

    
####################################################################

twisted_knobs = defaultdict(list)

####################################################################

while True:
    midievent(0xB0, 32, 1).send(True) # bank 100+
    midievent(0xC0, 80).send(True) # ominous gram
    midievent(0xC0, 81).send(True) # ominous gram
    # Patch change takes a bit; sleep till synth is ready again.
    time.sleep(0.5)

    try:
        print("play")
        tick_target = 0
        played_ticks = 0
        tempo = 1
        start = time.time()
        last_time = start
        note_idx = 0
        capt = CapT()
        while True:
            # how much time has passed?
            now = time.time()
            delta = now - last_time
            last_time = now

            current_tps = TICKS_PER_SEC * tempo
            tick_target += current_tps * delta

            time.sleep(0.010001)

            # Gather any notes ready to be played
            ticks_to_play = 0
            while True and note_idx < len(notes):
                if played_ticks + ticks_to_play >= tick_target:
                    played_ticks += ticks_to_play
                    break
                note = notes[note_idx]
                ticks_to_play += note.ticks
                # print( "ADDING:", ticks_to_play, note.ticks,)
                note_idx += 1

                # send midi note
                note.send()

                # send osc note
                if note.msg[2] > 0: 
                  client.send_message("/note_on", note.msg)
                  print("note on", note.msg)
                else:
                  client.send_message("/note_off", note.msg)
                  print("note off", note.msg)
                # client.send_message("/play_note", note.msg)

            if note_idx >= len(notes):
                note_idx = 0

            # Sensors
            if capt:
                # if the cap touch is broken, could get stuck waiting here...
                touches = capt.get_in_touch()

                result_list_by_knob = defaultdict(list)

                for touch_val, cap_list in zip(touches, caps):
                    for cap in cap_list:
                        knob, val, touched, minval = cap.get_out(touch_val)

                        # if touched > 0:
                        # print ("touched          ", knob, val, touched)

                        if knob is TEMPO and touched > 0:
                            _tempo = val / TICKS_PER_SEC
                            # result_list_by_knob[TEMPO].append(_tempo)
                            result_list_by_knob[knob].append(_tempo)
                            # midievent(0xB0, knob, _tempo).send(True)
                        elif touched > 0:
                            # print ("%%%%%%%%midi event%%%%%%%%%%          ", knob, val, touched)
                            result_list_by_knob[knob].append(val)
                            twisted_knobs[knob] = val

                            # send midi cc
                            midievent(0xB0, knob, val).send(True)

                            # send cc message via osc
                            path = find_osc_path_by_knob(knob)
                            # print("path", path)
                            if path == "/f 1" and val>0.51:
                              # print("set q")
                              client.send_message("/params/q 1", 0.5)
                              client.send_message("/params/f 1", random.random()/2)
                              client.send_message("/params/f 2", random.random()/2)
                              # client.send_message("/params/f 2", 1-val)
                              client.send_message("/params/q 2", 0.5)
                            elif path == "/ratios":
                              client.send_message("/ratios", 1)
                            elif path == "/pms":
                              print("pms on")
                              client.send_message("/pms", 1)
                            elif path:
                              client.send_message("/params"+path, val)
                            # else:
                            #   print("no path found!")


                        else:
                          # for knob, results in twisted_knobs.items():
                            # print ("%%%%%%%%midi off event%%%%%%%%%%          ", knob, val, touched, twisted_knobs[knob])
                            # print(twisted_knobs[knob] == 0)
                          if twisted_knobs[knob] != minval:
                            # print("clear knob", knob, minval)
                            twisted_knobs[knob] = minval

                            # send midi cc off
                            midievent(0xB0, knob, minval).send(True)

                            # send off cc message via osc
                            path = find_osc_path_by_knob(knob)
                            if path == "/f 1":
                              print("clear q")
                              client.send_message("/params/q 1", 0)
                              client.send_message("/params/q 2", 0)
                            elif path == "/ratios":
                              print("clear ratios")
                              client.send_message("/ratios", 0)
                            elif path == "/pms":
                              print("clear pm")
                              client.send_message("/pms", 0)
                            elif path:
                              client.send_message("/params"+path, minval)
                            
                            cap.reset_to_min()


                            # else:
                            #   print("no path found!")


                        # else:
                        #   for knob, results in twisted_knobs.items():
                        #     if twisted_knobs[knob] > 0:
                        #       # print("untouchted",knob)
                        #       midievent(0xB0, knob, 0).send(True)

                            
                #print(result_list_by_knob)
                # print(twisted_knobs)


                # for knob, results in result_list_by_knob.items():
                #   print("results",results)
                #   max_val = max(results)
                #   if knob is TEMPO:
                #     tempo = max_val
                #   else:
                #       print ("%%%%%%%%midi event%%%%%%%%%%          ", knob, val, touched)
                #       # midievent(0xB0, knob, max_val).send(True)
                #       midievent(0xB0, knob, results[0]).send(True)
                #       time.sleep(1)
                #       midievent(0xB0, knob, 0).send(True)
                #       print ("zeroed", knob, touched)



    except KeyboardInterrupt:
        all_midi_off()
        break

midievent(0x80,  123, 0).send()
