#!/usr/bin/python

import sys, argparse, time
from ev3dev import *

lmotor = large_motor(OUTPUT_C); assert lmotor.connected
rmotor = large_motor(OUTPUT_B); assert rmotor.connected
armmotor = medium_motor(OUTPUT_D); assert armmotor.connected

ts = touch_sensor(); 		assert ts.connected
cs     = color_sensor();	assert cs.connected
ls = light_sensor();		assert ls.connected
irs = infrared_sensor();	assert irs.connected

cs.mode = 'RGB-RAW'
ls.mode = 'REFLECT'
irs.mode = 'IR-PROX'

def daj_kolor(R, G, B):
	print("G/R B/R G/B %s %s %s" %((G/R), (B/R), (G/B)))
	if((G/R > 1.1 and G/R < 2.1)and(B/R > 0.8 and B/R < 1.5)and(G/B > 1.0 and G/B < 2.1)): print("szary")
	elif((G/R > 0.25 and G/R < 1.1)and(B/R > 0.10 and B/R < 0.8)and(G/B > 1.5 and G/B < 2.7)): print("czerwony")
	elif((G/R > 1.3 and G/R < 1.5)and(B/R > 0.20 and B/R < 0.8)and(G/B > 1.5 and G/B < 6.0)): print("yello")
	elif((G/R > 1.9 and G/R < 4.1)and(B/R > 1.5 and B/R < 5.0)and(G/B > 0.5 and G/B < 1.3)): print("niebieski")
	elif((G/R > 2.1 and G/R < 6.0)and(B/R > 1.2 and B/R < 2.2)and(G/B > 1.5 and G/B < 3.1)): print("grun")
	else: print("kolor")

def get_reading(color, a):
    v = a.value()
    print("%s: %s" %(color, v))
    return v

armmotor.speed_regulation_enabled = 'on'

test = 0x00

while True:
	if(ts.value()):
		L = float(ls.value()-325)/224
		#C = float(cs.value()-3)/21
		if (L < 0 ): L = 0
		if (L > 1 ): L = 1
		#if (C < 0 ): C = 0
		#if (C > 1 ): C = 1
		#print("swiatla: %s" %(L))
		#print("swiatlaL %s" %(ls.value()))
		print("R: %s" %(cs.value(0)))	
		print("G: %s" %(cs.value(1)))
		print("B: %s" %(cs.value(2)))
		daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
		#print("swiatla: %s" %(L))
		#print("Suma: %s" %(cs.value(0)+cs.value(1)+cs.value(2))) #powyzej 380 - bialy, ponizej 100 czarny
		#print("Odleglosc: %s" %(irs.value())) #przy 8 jest przed kulka
		#print("pozycja reki: %s" %(armmotor.position))

		#print("0x00: %s" %(test))
		#print("0x01: %s" %(0x01))
		#print("0x02: %s" %(0x02))
		#print("0x01 or 0x02: %s" %(0x01|0x02))
		#print("0x03 xor 0x01: %s" %(0x03^0x01))
		
		#armmotor.speed_sp = 100
		#armmotor.run_to_abs_pos(position_sp = -18)
		#armmotor.run_to_abs_pos(position_sp=-2) #pozycja na dole -28
		#armmotor.run_to_abs_pos(position_sp = 70) #pozycja na gorze 23
		time.sleep(0.1)
