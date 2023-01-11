import random
import sys
import time

import rtmidi

class mymidi(object):

    magic_midi_strings = [
        # 'MIDIPLUS TBOX 2x2:MIDIPLUS TBOX 2x2 MIDI 1 20:0',
        # 'MIDILINK-mini:MIDILINK-mini MIDI 1 20:0',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 1 20:0',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 1 20:1',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 2 20:0',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 2 20:1',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 1 24:0',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 1 24:1',
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 1 32:0', 
        # 'ESI MIDIMATE eX:ESI MIDIMATE eX MIDI 2 32:1',
        # 'QT-2host:QT-2host MIDI 1 24:0',
        # 'QT-2host:QT-2host MIDI 1 20:0',	      
	      'twohost:twohost MIDI 1 20:0',
        'twohost:twohost MIDI 1 28:0',
        
    ]

    def __init__(self):
        self.midiout = rtmidi.MidiOut()
        self.midi_device_connected = False
        self.midi_device_connected = self.start()
        print("midi_device_connected",self.midi_device_connected)


    def start(self):
        available_ports = self.midiout.get_ports()
        for midi_name in self.magic_midi_strings:
            try:
                idx = available_ports.index(midi_name)
                self.midiout.open_port(idx)
                return True
            except:
                pass

                print( "Couldn't open midi!")
                print( "Looking for port in: '%s'" % self.magic_midi_strings)
                print( "But only found: %s" % available_ports)
                print()
                print( "Make sure everything is plugged in.")

                # time.sleep(1)
                # sys.exit()
                return False

    def send_message(self, msg):
      if self.midi_device_connected == True:
        self.midiout.send_message(msg)
        if msg[0] == 144: 
          time.sleep(0.5)
          self.midiout.send_message([0x80,msg[1],0])
          # print("off",0x80,msg[1],0)


# class mymidi(object):
#     magic_midi_string = 'MIDIPLUS TBOX 2x2:MIDIPLUS TBOX 2x2 MIDI 1 20:0'
#
#     def __init__(self):
#         self.midiout = rtmidi.MidiOut()
#         self.start()
#
#     def start(self):
#         available_ports = self.midiout.get_ports()
#
#         idx = available_ports.index(self.magic_midi_string)
#
#         try:
#             self.midiout.open_port(1)
#         except:
#             print "Couldn't open midi!"
#             print "Looking for port: '%s'" % self.magic_midi_string
#             print "But only found: %s" % available_ports
#             print
#             print "Make sure everything is plugged in."
#
#             sys.exit()
#     def send_message(self, msg):
#         self.midiout.send_message(msg)


class midievent(object):
    midiout = None

    @classmethod
    def set_midiout(cls, mo):
        cls.midiout = mo

    def __init__(self, mc, code, data=None, ticks=0):
        self.msg = [mc, code]
        if data is not None:
            if isinstance(data, list):
                self.msg.extend(data)
            else:
                self.msg.append(data)

        self.ticks = ticks

    def send(self, p=False):
        # print("p",p)
        
        # if p:
        #     print( self.msg)

        self.midiout.send_message(self.msg)


def all_midi_off():
    mm = mymidi()
    midievent.set_midiout(mm)
    print ("all off!!!")
    midievent(0xB0, 0x7B, 0).send()
    midievent(0xB0, 0x78, 0).send()
