#!/usr/bin/env python3
########################################################################
# Filename    : piClock.py
# Description : horloge numérique
# auther      : papsdroid.fr
# modification: 2020/03/13
########################################################################

import RPi.GPIO as GPIO
import time, threading, os, board, neopixel
from datetime import datetime
from random import randrange
from adafruit_ht16k33.segments import BigSeg7x4

#-----------------------------------------------------
# classe de gestion d'un anneau de 60 leds Neopixels
#-----------------------------------------------------
class RingLeds():
    def __init__(self, nb_leds):
        self.pixel_pin = board.D18       # GPIO18 envoie les commandes au ruban
        self.nb_leds = nb_leds           # nb de leds du ruban
        self.pixels = neopixel.NeoPixel(self.pixel_pin, self.nb_leds, brightness=0.1, auto_write=False, pixel_order=neopixel.GRB)
        self.hh = datetime.now().strftime('%H')
        self.mn = datetime.now().strftime('%M')
        self.secondes = int(datetime.now().strftime('%S'))  # secondes à afficher
        self.rgbc1 = 0xFF0000          # couleur rouge RGB
        self.rgbc2 = 0x1d0221          # couleur violette RGB
        self.rgbHhigh  = 0xff0000      # couleur pour les heures
        self.rgbHmedium = 0xff4300     # couleur pour les heures 
        self.rgbHlow  = 0xff742c       # couleur pour les heures
        self.rgbM  = 0x008000          # couleur pour les minutes
        self.rgbS  = 0x000080          # couleur pour les secondes 
        self.rgbMIN = 10       	       # minimum pour générer un niveau de  couleur au hasard entre 0 et 255
        self.rgbMAX = 127              # maximum pour générer un niveau de  couleur au hasard entre 0 et 255 
        self.anims_secondes = ['self.ledn_wheel_on()', 'self.ledn_red_on()', 'self.ledn_random_on()','self.ledn_randomB_on()',
			           'self.ledn_randomR_on()','self.ledn_randomG_on()']
        self.anims = ['self.ledn_anim_secondes()', 'self.time()', 'self.pause()']
        self.id_anim=0                   # référence de l'animation leds, incrémentée avec le bouton poussoir
        self.id_pause = 2                # id animation pause
        self.id_anim_secondes = 0        # référence de l'animation leds secondes en cours, modifiée toutes les minutes
        self.change_anim_secondes = False # état du changement d'animation des secondes
        self.actif = True                # True: anneau actif
        self.init = True                 # True: allume toutes les leds de rang <= secondes en cours
                                         # False: allume uniquement la led de rang = secondes en cours
    #mise à jour des secondes et animation anneau de leds
    #----------------------------------------------------
    def set_time(self, hh,mn,ss):
        self.hh, self.mn, self.secondes = hh, mn, ss
        if (self.id_anim < len(self.anims)-2) and (self.secondes == 0) :
            self.led_anim_off()         # animation pour éteindre toutes les leds sur les animations de type secondes
        exec(self.anims[self.id_anim])  # animation correspondante à id_anim

    def ledn_anim_secondes(self):
        exec(self.anims_secondes[self.id_anim_secondes])         # animation correspondant à  id_anim_secondes
        if self.change_anim_secondes and self.secondes == 0:      # changement d'animation toutes les minutes si pas déjà changé
            self.id_anim_secondes_suivant()
            self.change_anim_secondes = False
        if not(self.change_anim_secondes) and self.secondes > 0:
            self.change_anim_secondes = True

    # gestion des animations en boucle
    #-----------------------------------
    def id_anim_suivant(self):
        self.id_anim = (self.id_anim+1) %  len(self.anims)
        if self.id_anim == 0:
            self.actif=True
        self.init = True

    # gestion des animations secondes modifiées toutes les minutes
    # -----------------------------------------------------------
    def id_anim_secondes_suivant(self):
        self.id_anim_secondes = (self.id_anim_secondes + 1) % len(self.anims_secondes)

    #mise en pause du ruban de leds
    #----------------------------------------------
    def pause(self):
        self.actif=False
        self.off()

    #extinction des leds
    #----------------------------------------------
    def off(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    #détermine les leds à allumer [debut, fin[ en fonction de self.init
    #------------------------------------------------------------------
    def slotLeds(self):
        debut, fin = self.secondes, self.secondes+1
        if self.init:
            debut = 0
            self.init = False
        return debut, fin

    #allume la led de rang n=secondes avec une couleur arc-en-ciel indexée par n
    #------------------------------------------------------------------
    def ledn_wheel_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            pixel_index = (l * 256 // self.nb_leds)
            self.pixels[l] = self.wheel(pixel_index & 255)
        self.pixels.show()

    #allume la led de rang n avec une couleur self.rgbRED
    #----------------------------------------------------
    def ledn_red_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            if (l%2==0):
                self.pixels[l] = self.rgbc1
            else:
                self.pixels[l] = self.rgbc2
        self.pixels.show()

    #allume la led de rang n avec une couleur au hasard
    #--------------------------------------------------
    def ledn_random_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            r,g,b = 0,0,0
            while (r+g+b) <= self.rgbMIN :
                r,g,b = randrange(0,self.rgbMAX), randrange(0,self.rgbMAX), randrange(0, self.rgbMAX)
            self.pixels[l] = [r,g,b]
            #self.pixels[l] = [self.rgbMIN, 0,0]
        self.pixels.show()

    #allume la led de rang n avec une couleur sauf BLEUE au hasard
    #--------------------------------------------------------------
    def ledn_randomB_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            r,g,b = 0,0,0
            while (r+g+b) <= self.rgbMIN :
                r,g,b = randrange(self.rgbMIN,self.rgbMAX), randrange(self.rgbMIN,self.rgbMAX), 0
            self.pixels[l] = [r,g,b]
        self.pixels.show()

    #allume la led de rang n avec une couleur sauf ROUGE  au hasard
    #--------------------------------------------------------------
    def ledn_randomR_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            r,g,b = 0,0,0
            while (r+g+b) <= self.rgbMIN :
                r,g,b = 0, randrange(0,self.rgbMAX), randrange(0,self.rgbMAX)
            self.pixels[l] = [r,g,b]
        self.pixels.show()

    #allume la led de rang n avec une couleur VERTE  au hasard
    #--------------------------------------------------
    def ledn_randomG_on(self):
        debut, fin = self.slotLeds()
        for l in range(debut, fin):
            r,g,b = 0,0,0
            while (r+g+b) <= self.rgbMIN :
                r,g,b = randrange(0, self.rgbMAX), 0, randrange(0, self.rgbMAX)
            self.pixels[l] = [r,g,b]
        self.pixels.show()

    #affiche heure, minutes et secondes sur le cadran
    def time(self):
        rang_hh, rang_mn = int(self.hh)%12, int(self.mn)
        rang_hh = int(self.nb_leds*(rang_hh+rang_mn/60)/12)
        rang_hhP, rang_hhM = (rang_hh-2)%self.nb_leds, (rang_hh-1)%self.nb_leds
        rang_mn = int(self.nb_leds*rang_mn/60)
        self.pixels.fill((0, 0, 0))
        self.pixels[rang_hh] = self.rgbHhigh
        self.pixels[rang_hhP] = self.rgbHlow
        self.pixels[rang_hhM] = self.rgbHmedium
        self.pixels[rang_mn] = self.rgbM
        self.pixels[self.secondes] = self.rgbS
        self.pixels.show()

    #etteint progressivement les leds dans le sens inverse des aiguilles d'une montre
    #--------------------------------------------------------------------------------
    def led_anim_off(self):
        for i in range(self.nb_leds-1,0,-1):
            self.pixels[i] = [0,0,0]
            self.pixels.show()
            time.sleep(0.001)

    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    # ----------------------------------------------------
    def wheel(self, pos):
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (r, g, b)

#------------------------------------------------------------------
# classe de gestion de l'afficheur 7 segment Adagruit avec backpack
#------------------------------------------------------------------
class SevenDisplay():
    def __init__(self):
        self.i2c = board.I2C()
        self.display = BigSeg7x4(self.i2c)
        self.display.brightness = 0.4
        self.display.blink_rate = 0
        self.hh = "00"     # heure
        self.mn = "00"     # minutes
        self.off()         # étteint l'afficheur 7 segments au démarrage

    #mise à jour de l'heure
    #------------------------------
    def set_time(self, hh, mn, ss, ds):
        if ds <5 :      # dixième de secondes: fait clignoter le séparateur toutes les 1/2 secondes
            self.display.colon = True
        else:
            self.display.colon = False
        self.display.print(hh+mn)
        self.display.show()

    # extinction de l'afficheur
    #----------------------------------------------
    def off(self):
        self.display.fill(0)
        self.display.show()

#--------------------------------------------------------------------------------------------------
# class Timer(thread): gère l'affichage du temps sur l'anneau de leds et l'afficheur 7 segments
#--------------------------------------------------------------------------------------------------
class Timer(threading.Thread):
    def __init__(self, ringLeds, display):
        threading.Thread.__init__(self)  # appel au constructeur de la classe mère Thread
        self.etat=False               # True: thread démarré
        self.ringLeds = ringLeds         # anneau de leds pour afficher les secondes
        self.display = display           # afficheur 7 segments pour afficher hh et mn
        self.hh = "00"     # heure
        self.mn = "00"     # minutes
        self.ss = 0        # secondes
        self.ds = 0        # dixièmes de secondes
        self.start()       # démarrage du thread

    #maj heure du timer
    #------------------------------
    def set_time(self, hh,mn,ss, ds):
        self.hh, self.mn, self.ss, self.ds = hh, mn,ss , ds

    #extinction du timer
    #-------------------
    def off(self):
        self.display.off()
        self.ringLeds.off()

    #exécution du thread
    #-------------------
    def run(self):
        self.off()
        self.etat = True
        while (self.etat):
            if self.ringLeds.actif:
                self.ringLeds.set_time(self.hh, self.mn, self.ss)
                #self.ringLeds.set_time("12","18",self.ss") # tests
            self.display.set_time(self.hh, self.mn, self.ss, self.ds)
            time.sleep(0.1)
        self.off()

    #arrêt du thread (ne peut plus redémarrer après)
    #----------------------------------------------
    def stop(self):
        self.etat=False


#classe d'Application principale
#------------------------------------------------------------------------------------------------------
class Application:
    def __init__(self):
        print("démarrage piCLock")
        self.display = SevenDisplay()                # affichage 7 segments
        self.leds = RingLeds(60)                     # rubans de 60 leds
        self.timer = Timer(self.leds, self.display)  # thread timer 
        self.buttonSelectPin = 20       # bouton pour changement d'animation
        self.buttonOffPin = 21          # bouton d'extinction
        #pin associés aux boutons poussoirs
        GPIO.setup(self.buttonSelectPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)     # mode INPUT, pull_up=high
        GPIO.setup(self.buttonOffPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        # mode INPUT, pull_up=high
        GPIO.add_event_detect(self.buttonSelectPin,GPIO.FALLING,callback = self.buttonSelectEvent, bouncetime=300)
        GPIO.add_event_detect(self.buttonOffPin,GPIO.FALLING,callback=self.buttonOffEvent, bouncetime=300)

    #méthode de destruction
    def destroy(self):
        print ('bye')
        self.timer.stop() # arrêt du thread timer
        time.sleep(1)
        GPIO.cleanup()

    #bouton poussoir SELECT: change l'animation du ruban de leds.
    #-------------------------------------------------------------
    def buttonSelectEvent(self,channel):
        self.leds.id_anim_suivant()
        #print('Select pressed',self.leds.id_anim )

    #bouton poussoir OFF: extinction système
    #----------------------------------------
    def buttonOffEvent(self,channel):
        print('Extinction du système')
        self.timer.stop()
        self.timer.off()
        os.system('sudo halt') #provoque l'extinction du Raspberry pi

    #boucle principale du prg
    def loop(self):
        while True:
            now = datetime.now()
            hh = now.strftime('%H')      # heure sur 2 chiffres
            mn = now.strftime('%M')      # minutes sur 2 chiffres
            ss = now.strftime('%S')      # secondes converties en entier
            ds = now.strftime('%f')[0]   # 1er unités des microsecondes sur 6 chiffres (1/10 secondes)
            #print('time:', hh,mn,ss, ms)
            if self.timer.ringLeds.actif and hh == '00':     # mise en pause automatique du ruban de leds à minuit
                self.timer.ringLeds.id_anim = self.timer.ringLeds.id_pause
            self.timer.set_time(hh,mn,int(ss),int(ds))
            time.sleep(0.1)

if __name__ == '__main__':
    appl=Application() 
    try:
        appl.loop()
    except KeyboardInterrupt:  # interruption clavier CTRL-C: appel à la méthode destroy() de appl.
        appl.destroy()


