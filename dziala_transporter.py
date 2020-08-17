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

def get_reading(color):
    while not ts.value(): time.sleep(0.1)


    v = ls.value()
    print("%s: %s" %(color, v))
    return v

def daj_kolor(R, G, B):
	if(R == 0): R = 1
	if(G == 0): G = 1
	if(B == 0): B = 1
	if((G/R > 1.1 and G/R < 2.1)and(B/R > 0.8 and B/R < 1.5)and(G/B > 1.0 and G/B < 2.1)):
		if((R+G+B)> 400): return 0 #bialy
		else: return 1 #czarny
	elif((G/R > 0.25 and G/R < 1.1)and(B/R > 0.10 and B/R < 0.8)and(G/B > 1.5 and G/B < 2.7)):
		#print("czerwony")
		return 2	#czerwony
	elif((G/R > 1.3 and G/R < 1.5)and(B/R > 0.20 and B/R < 0.8)and(G/B > 1.5 and G/B < 6.0)):
		#print("yello")
		return 3	#zolty
	elif((G/R > 1.9 and G/R < 4.1)and(B/R > 1.5 and B/R < 5.0)and(G/B > 0.5 and G/B < 1.3)):
		#print("niebieski")
		return 4	#niebieski
	elif((G/R > 2.1 and G/R < 6.0)and(B/R > 1.2 and B/R < 2.2)and(G/B > 1.5 and G/B < 3.1) and (G > 50)):
		#print("grun")
		return 5	#zielony
	else: return -1


def wait():
    while(lmotor.state.count('running') or rmotor.state.count('running')):
        time.sleep(0.01)
        
white = get_reading('white')
black = get_reading('black')
mid   = 0.5 * (white + black)

while not (ts.value()): time.sleep(0.01)

on = False;
licznik = 0;
licznik1 = 0;
licznik2 = 0;
historia_koloru = -1;
aktualny_cel = -1;
znalazlem_bialy_stan_11 = False
czerwony = False
bitowa_historia_koloru = 0x00

#1 - w lewo, 2 - w prawo
historia_skretu = -1

wykrylem_kulke = False

#stany
#0 - poszukiwanie bazy z pilka
#1 - znaleziono baze
#2 - skret w lewo
#3 - skret w prawo
#4 - jazda do bazy ze skretu
#5 - szukanie kulki
stan = 0; 

lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'
armmotor.speed_regulation_enabled = 'on'
armmotor.speed_sp = 200
armmotor.run_to_abs_pos(position_sp = 23)

lspeed = 100
rspeed = 100

last_error1 = 0
last_error2 = 0
last_error3 = 0

integral   = 0



while True:
	if(ts.value()):
		on = True
		time.sleep(0.5)
	lmotor.run_forever(speed_sp=0)
	rmotor.run_forever(speed_sp=0)
	while on:
		if(stan == 0):
			L = float(ls.value()-325)/224
			if (L < 0 ): L = 0
			if (L > 1 ): L = 1
			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0):
				licznik = licznik + 1
			else: licznik = 0

			error      = 0.5 - L
			integral   = integral + error*0.001
			derivative = (error + 3*last_error1 - 3*last_error2 - last_error3)/6
			last_error3 = last_error2
			last_error2 = last_error1
			last_error1 = error
		
			if(licznik > 2):
				correction = 1.5 * error + 0.5 * integral + 2.0 * derivative
				lspeed	= int(-100 - 400*correction)
				rspeed = int(-100 + 400*correction)
			else:
				correction = 0.6 * error + 0.2 * integral + 0.3 * derivative #zwiekszyc P (chyba)
				lspeed	= int(-250 - 400*correction)
				rspeed = int(-250 + 400*correction)
			
			if (lspeed > 800): 
					lspeed = 800
			if (lspeed < -800):
					lspeed = -800
			if (rspeed > 800):
					rspeed = 800 
			if (rspeed < -800):
					rspeed = -800

			lmotor.run_forever(speed_sp=lspeed)
		   	rmotor.run_forever(speed_sp=rspeed)
			
			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 5 and historia_koloru == 5):
				stan = 1 #wykryto baze
				licznik = 0
				licznik1 = 0
				historia_koloru = -1;
			elif(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 2 and historia_koloru == 2):
				czerwony = True
				licznik1 = 20
				historia_koloru = -1;	

			historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))						

		#znaleziono baze
		elif(stan == 1):
			if(licznik < 150):
				lmotor.run_forever(speed_sp=-80)
			   	rmotor.run_forever(speed_sp=60)
				licznik = licznik + 1
			elif(licznik < 152):
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = licznik + 1

				historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
				
			elif(licznik < 302):
				lmotor.run_forever(speed_sp=80)
			   	rmotor.run_forever(speed_sp=-60)
				licznik = licznik + 1
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = 0;
				if(historia_koloru == 0):
					stan = 2 #skret w lewo
					historia_koloru = -1
				else:
					stan = 3 #skret w prawo
					historia_koloru = -1
		#skret w lewo		
		elif(stan == 2):
			if(licznik < 170):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 270):
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 400):
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				if (not(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0)):
					licznik = 0
					historia_koloru = -1
					historia_skretu = 1
					stan = 4 #jazda do bazy ze skretu w lewo
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
		#skret w prawo
		elif(stan == 3):
			if(licznik < 130):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 230):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
			elif(licznik < 400):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if (not(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0)):
					licznik = 0
					historia_koloru = -1
					historia_skretu = 2
					stan = 4 #jazda do bazy ze skretu w prawo
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
		#dojazd do bazy
		elif(stan == 4):
			L = float(ls.value()-325)/224
			if (L < 0 ): L = 0
			if (L > 1 ): L = 1
			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0):
				licznik = licznik + 1
			else: licznik = 0

			error      = 0.5 - L
			integral   = integral + error*0.001
			derivative = (error + 3*last_error1 - 3*last_error2 - last_error3)/6
			last_error3 = last_error2
			last_error2 = last_error1
			last_error1 = error
		
			if(licznik > 3):
				correction = 1.5 * error + 0.5 * integral + 2.0 * derivative
				lspeed	= int(-100 - 400*correction)
				rspeed = int(-100 + 400*correction)
			else:
				correction = 0.6 * error + 0.2 * integral + 0.3 * derivative #zwiekszyc P (chyba)
				lspeed	= int(-150 - 400*correction)
				rspeed = int(-150 + 400*correction)
		
			if (lspeed > 800): 
					lspeed = 800
			if (lspeed < -800):
					lspeed = -800
			if (rspeed > 800):
					rspeed = 800 
			if (rspeed < -800):
					rspeed = -800
	
			lmotor.run_forever(speed_sp=lspeed)
		   	rmotor.run_forever(speed_sp=rspeed)	


			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 2 and historia_koloru == 2):
				stan = 5 #wyszukiwanie kulki
				licznik = 0
				historia_koloru = -1
				aktualny_cel = 2	
			elif(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 4 and historia_koloru == 4):
				stan = 5 #wyszukiwanie kulki
				licznik = 0
				historia_koloru = -1
				aktualny_cel = 4
			elif(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 3 and historia_koloru == 3):
				stan = 5 #wyszukiwanie kulki
				licznik = 0
				historia_koloru = -1
				aktualny_cel = 3


			historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))	
		#szukanie kulki
		elif(stan == 5):			
			if(licznik < 50):
				#print("<50")
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if(wykrylem_kulke):
					licznik = 850
				if(irs.value() < 9 ):
					wykrylem_kulke = True
					armmotor.run_to_abs_pos(position_sp = -13)
					licznik = 850
					
			elif(licznik < 150):
				#print("<150")
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 350):
				#print("<350")
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 450):
				#print("<450")
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 500):
				#print("<500")
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 600):
				#print("<600")
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 800):
				#print("<800")
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				if(irs.value() < 15 ):
					licznik = 800
			elif(licznik < 850):
				#print("<850")
				lmotor.run_forever(speed_sp=-250)
			   	rmotor.run_forever(speed_sp=-250)
				licznik = licznik + 1
				if(irs.value() < 9 ):
					wykrylem_kulke = True
					armmotor.run_to_abs_pos(position_sp = -13)
					licznik = 850
			elif(licznik < 950):
				#print("<950")
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = licznik + 1
				if(licznik == 950 and wykrylem_kulke == False):
					armmotor.run_to_abs_pos(position_sp = -13)
					wykrylem_kulke = True
			elif(licznik < 1900 and wykrylem_kulke == True):
				#print("<1900")
				lmotor.run_forever(speed_sp=+200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				tmp = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
				if ((tmp == 1 or tmp == 5) and licznik >1020):
					licznik = 0
					historia_koloru = -1
					stan = 6 #jazda do celu

			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				#print("dupa")

		#jazda do celu
		elif(stan == 6):
			L = float(ls.value()-325)/224
			if (L < 0 ): L = 0
			if (L > 1 ): L = 1
			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0):
				licznik = licznik + 1
			else: licznik = 0

			error      = 0.5 - L
			integral   = integral + error*0.001
			derivative = (error + 3*last_error1 - 3*last_error2 - last_error3)/6
			last_error3 = last_error2
			last_error2 = last_error1
			last_error1 = error
		
			if(licznik > 2):
				correction = 1.5 * error + 0.5 * integral + 2.0 * derivative
				lspeed	= int(-100 - 400*correction)
				rspeed = int(-100 + 400*correction)
			else:
				correction = 0.6 * error + 0.2 * integral + 0.3 * derivative #zwiekszyc P (chyba)
				lspeed	= int(-250 - 400*correction)
				rspeed = int(-250 + 400*correction)
		
			if (lspeed > 800): 
					lspeed = 800
			if (lspeed < -800):
					lspeed = -800
			if (rspeed > 800):
					rspeed = 800 
			if (rspeed < -800):
					rspeed = -800
	
			lmotor.run_forever(speed_sp=lspeed)
		   	rmotor.run_forever(speed_sp=rspeed)
			
			if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == aktualny_cel and historia_koloru == aktualny_cel):
				stan = 7 #wykryto cel
				licznik = 0
				historia_koloru = -1;	

			historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
		
		#skret do celu		
		elif(stan==7):
			if(licznik < 150):
				lmotor.run_forever(speed_sp=-80)
			   	rmotor.run_forever(speed_sp=60)
				licznik = licznik + 1
			elif(licznik < 152):
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = licznik + 1

				historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
				
			elif(licznik < 302):
				lmotor.run_forever(speed_sp=80)
			   	rmotor.run_forever(speed_sp=-60)
				licznik = licznik + 1
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = 0;
				if(historia_koloru == 0):
					stan = 8 #skret w lewo
					historia_koloru = -1
				else:
					stan = 9 #skret w prawo
					historia_koloru = -1
		#skret w lewo	do celu	
		elif(stan == 8):
			if(licznik < 170):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 270):
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 400):
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				if (not(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0)):
					licznik = 0
					historia_koloru = -1
					historia_skretu = 1
					stan = 10 #jazda do bazy ze skretu w lewo
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
		#skret w prawo do celu
		elif(stan == 9):
			if(licznik < 130):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
			elif(licznik < 230):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
			elif(licznik < 400):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
				if (not(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0)):
					licznik = 400
					
			elif(licznik < 420):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
			else:
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				historia_koloru = -1
				historia_skretu = 2
				stan = 10 #jazda do bazy ze skretu w prawo
		#dojazd do celu
		elif(stan == 10):
			if((aktualny_cel == 2 or aktualny_cel == 3) and licznik2 < 100):
				lmotor.run_forever(speed_sp=-200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik2 = licznik2 + 1
			else:
				L = float(ls.value()-325)/224
				if (L < 0 ): L = 0
				if (L > 1 ): L = 1
				if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0):
					licznik = licznik + 1
				else: licznik = 0

				error      = 0.5 - L
				integral   = integral + error*0.001
				derivative = (error + 3*last_error1 - 3*last_error2 - last_error3)/6
				last_error3 = last_error2
				last_error2 = last_error1
				last_error1 = error
		
				if(licznik > 3):
					correction = 1.5 * error + 0.5 * integral + 2.0 * derivative
					lspeed	= int(-100 - 400*correction)
					rspeed = int(-100 + 400*correction)
				else:
					correction = 0.6 * error + 0.2 * integral + 0.3 * derivative #zwiekszyc P (chyba)
					lspeed	= int(-150 - 400*correction)
					rspeed = int(-150 + 400*correction)
		
				if (lspeed > 800): 
						lspeed = 800
				if (lspeed < -800):
						lspeed = -800
				if (rspeed > 800):
						rspeed = 800 
				if (rspeed < -800):
						rspeed = -800
	
				lmotor.run_forever(speed_sp=lspeed)
			   	rmotor.run_forever(speed_sp=rspeed)
			
			
				if((licznik1 > 50) and (daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == aktualny_cel) and (historia_koloru == aktualny_cel)):
					stan = 11 #oddanie i powrot do 0
					licznik = 0
					licznik1 = 0
					licznik2 = 0
					historia_koloru = -1
					wykrylem_kulke = False

				historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))	
				licznik1 = licznik1 + 1

		elif(stan==11):
			if(licznik < 50):
				lmotor.run_forever(speed_sp=0)
			   	rmotor.run_forever(speed_sp=0)
				licznik = licznik + 1
				armmotor.run_to_abs_pos(position_sp = 23)
			elif(licznik < 120):
				lmotor.run_forever(speed_sp=200)
			   	rmotor.run_forever(speed_sp=200)
				licznik = licznik + 1
			elif(licznik < 920):
				lmotor.run_forever(speed_sp=+200)
			   	rmotor.run_forever(speed_sp=-200)
				licznik = licznik + 1
				tmp = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))
				if(tmp == 0):
					znalazlem_bialy_stan_11 = True
				if ((znalazlem_bialy_stan_11 == True) and not(tmp == 0) and licznik > 250):
					licznik = 0
					historia_koloru = -1
					if(aktualny_cel == 2 or aktualny_cel == 3):
						czerwony = False
						licznik1 = 0
						stan = 12 #powrot na linie z czerwonego
					else:
						stan = 0
					aktualny_cel = -1

		#powrot na linie po czerwonym
		elif(stan==12):
			if(czerwony == True):
				if(licznik1 > 0):
					lmotor.run_forever(speed_sp=-200)
				   	rmotor.run_forever(speed_sp=-200)
					licznik1 = licznik1 - 1
				else:
					czerwony = False
					stan = 0
					licznik1 = 0
				
			else:

				if((daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 2 and historia_koloru == 2) or (daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 3 and historia_koloru == 3)):
					czerwony = True
					licznik1 = 150
					historia_koloru = -1;	

				historia_koloru = daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2)))				
	
				L = float(ls.value()-325)/224
				if (L < 0 ): L = 0
				if (L > 1 ): L = 1
				if(daj_kolor(float(cs.value(0)), float(cs.value(1)), float(cs.value(2))) == 0):
					licznik = licznik + 1
				else: licznik = 0

				error      = 0.5 - L
				integral   = integral + error*0.001
				derivative = (error + 3*last_error1 - 3*last_error2 - last_error3)/6
				last_error3 = last_error2
				last_error2 = last_error1
				last_error1 = error
		
				if(licznik > 3):
					correction = 1.5 * error + 0.5 * integral + 2.0 * derivative
					lspeed	= int(-100 - 400*correction)
					rspeed = int(-100 + 400*correction)
				else:
					correction = 0.6 * error + 0.2 * integral + 0.3 * derivative #zwiekszyc P (chyba)
					lspeed	= int(-200 - 400*correction)
					rspeed = int(-200 + 400*correction)	
		
				if (lspeed > 800): 
						lspeed = 800
				if (lspeed < -800):
						lspeed = -800
				if (rspeed > 800):
						rspeed = 800 
				if (rspeed < -800):
						rspeed = -800

				lmotor.run_forever(speed_sp=lspeed)
			   	rmotor.run_forever(speed_sp=rspeed)
			
			

		if(ts.value()): 
			on = False 
			last_error1 = 0
			last_error2 = 0
			last_error3 = 0
			integral   = 0
			stan = 0
			licznik = 0
			licznik1 = 0
			licznik2 = 0
			historia_koloru = 0
			historia_skretu = -1
			aktualny_cel = -1
			wykrylem_kulke = False
			armmotor.run_to_abs_pos(position_sp = 23)
			time.sleep(0.5)
		time.sleep(0.001)

