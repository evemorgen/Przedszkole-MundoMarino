# -*- coding: utf-8 -*-
# string = unicode(string, "utf-8") #string z polskimi znakami
_author__ = 'evemorgen'

import urllib2, os, pygame, time, socket

#prowizoryczny słownik randomowych imion i nazwisk skojarzonych z nr kart
TROLOLO = \
{
    "170.86.237.6"  :u"Adelajda Alinowska",
    #"202.116.237.6" :u"Bazyl Boberek",
    "154.126.246.6" :u"Czesław Czosnyka",
    "202.87.237.6"  :u"Dobrochna Dziączko",
    "250.115.237.6" :u"Ezechiel Echeński",
    "26.117.237.6"  :u"Fabiola Fiszko",
    "106.125.246.6" :u"Gerwazy Gwiździłł",
    "138.85.237.6"  :u"Hugona Hilc",
    "74.126.246.6"  :u"Ildefons Im",
    "225.58.245.196":u"Jakub Jakub",
    "52.79.142.184" :u"Kunegunda Kokocz",
}

listaDoWypiania = []                 # lista w której będą trzymane wszystkie nazwiska do wypisania
ostatnieSiedem = [0,0,0,0,0,0,0]     # lista ostatnich 7 które były wrzucone do wypisania
lastCardReaded = ""                  # numery ostaniej zczytanej karty
flagaZmianyKarty = 0                 # flaga mówiąca czy jest nowa karta
flagaTimeoutu = 0                    # flaga mówiąca o tym czy był timeout
liczbaOstatnichTimeoutow = 0         #
ostatnieZnalezione = 0               # do parsowania kilku rzeczy po sobie
iloscKart = 0                        # ilość zczytanych kart do tej pory
done = False                         # główna flaga dla maina

URLTIMEOUT = 3      # time out w sekundach
TIMEONSCREEN = 20   # ile czasu dane są na ekranie
HEIGHT = 768        # wysokość ekranu
WIDTH = 1360        # szerokość ekranu

#PWD = "/home/pi/pyPrzedszkole"                 #na raspi
#NAZWA_AUDIO = PWD + "/plum.wav"                #na raspi
#NAZWA_IKONA = PWD + "/Kindergarden.ico"        #na raspi
#NAZWA_CZCIONKA = PWD + "/Comic Sans MS.ttf"    #na raspi
NAZWA_AUDIO = "plum.wav"                        #na maku
NAZWA_IKONA = "Kindergarden.ico"                #na maku
NAZWA_CZCIONKA = "Comic Sans MS.ttf"            #na maku


#klasa trzymająca info o dzieciaku do wyświetlenia
class Person:
    timeCreated = 0                     # czas w którym zostało wyświetlone po raz pierwszy
    timeLeft = TIMEONSCREEN             # czas który jeszcze się będzie wyświetlać
    name = ""                           # string trzymający imie i nazwisko
    ifPrinted = 0                       # bool sprawdzający czy jest wypisywane
    def __init__(self, daneOsobowe):    # konstruktor
        self.name = daneOsobowe
    def printMe(self):                  # metoda powodująca rozpoczęcie countdownu
        if self.ifPrinted != 1:
            self.ifPrinted = 1
            self.timeCreated = now()
            pygame.mixer.music.play()
    def update(self):                   # metoda robiąca update czasu 'timeLeft'
        if self.ifPrinted == 1:
            self.timeLeft = TIMEONSCREEN - now() + self.timeCreated

#funkcja zwraca ilość tyknięć od kiedyśtam
#używana do porównywania czasu
def now():
    return int(time.time())

#parsowanie htmla pod kątem konkretnej rzeczy
#kodHTML, znak charakterystyczny (np znacznik przed <h1>), kolejny znak charaketerystyczny kończący dany string, opcjonalny arg
def parseHTML(html, czegoSzukamy, warStop,odKtorego=0):
    numerPocz = numerKon = html.find(czegoSzukamy,odKtorego) + len(czegoSzukamy)
    while html[numerKon] != warStop:
        numerKon += 1
    global ostatnieZnalezione
    ostatnieZnalezione = numerPocz
    return html[numerPocz:numerKon]

#odczytuje nową karte, tu są nie złe jaja
def getNewCard():
    try :       # ponieważ często są timeouty i wypluwane jest milion wyjątków to trzea to w try dać
        response = urllib2.urlopen('http://192.168.1.203',timeout=URLTIMEOUT) # tu se odczytuje html o ile nie mnie nie wyjebie
        html = response.read()                                                # właściwie to tu dopiero odczytuje
        global liczbaOstatnichTimeoutow
        global flagaTimeoutu
        global listaDoWypiania
        global ostatnieSiedem
        if flagaTimeoutu == 1 and False:
            global ostatnieZnalezione
            ostatnieZnalezione = 0
            for i in range(7):
                nowy = parseHTML(html,'<h1>Card ','<',ostatnieZnalezione)
                print nowy,
                if findOnLast7List(nowy) == 0:
                    dane = getNameFromID(nowy)
                    nowaOsoba = Person(dane)
                    if findOnList(nowaOsoba.name) == 0:                         # jeśli nie ma jeszcze na liście to WANIA DAWAJ
                        listaDoWypiania.append(nowaOsoba)                       # znaczy DODAWAJ.
                        ostatnieSiedem.append(nowy)
                        for i in range(7):
                            ostatnieSiedem[i] = ostatnieSiedem[i+1]
                        ostatnieSiedem.pop(7)                                   # tu odczytuje ile kart już zczytano
            print liczbaOstatnichTimeoutow
            print ostatnieSiedem
            flagaTimeoutu = 0
        else:
            liczbaOstatnichTimeoutow = 0
        numer = parseHTML(html,'<h1>Card ','<')                               # tu odczytuje ile kart już zczytano
        czas = parseHTML(html,'<h2>Time I\'m working fine -','<')             # tu odczytuje czas jaki działa czytnik
        ileKart = parseHTML(html,'<h3>How many cards readed? - ','<')         # tu czytam ile odczytano kart, tak, wiem, że ma być red
        global lastCardReaded
        if numer != lastCardReaded:
            global flagaZmianyKarty
            flagaZmianyKarty = 1
            lastCardReaded = numer
            global iloscKart
            iloscKart = ileKart
    except urllib2.URLError:                                                  # tu są wyjątki których jak nie obsłużę to wywala cały program
        flagaTimeoutu = 1
        liczbaOstatnichTimeoutow += 1
    except socket.timeout:
        flagaTimeoutu = 1
        liczbaOstatnichTimeoutow += 1

#funkcja która zamienia nr karty na dane osobowe
def getNameFromID(id):          #tu trzeba będzie pomęczyć Błacha o SQLA itd.
    start = id.find("- ") + 2
    if TROLOLO.has_key(id[start:len(id)]):
        imieNazwisko = TROLOLO[id[start:len(id)]] # wyciąganie prowizorycznej nazwy ze słownika
        return imieNazwisko
    else:
        return "Nieznana Karta"

#czyszczenie listy ze śmieci
def cleanList():
    global listaDoWypiania
    if len(listaDoWypiania) > 0:
        for i in range(len(listaDoWypiania) - 2): # z jakiegoś powodu tu działa len - 1
            if listaDoWypiania[i].timeLeft <= 0:
                listaDoWypiania.remove(listaDoWypiania[i])
        if listaDoWypiania[0].timeLeft <= 0:
            listaDoWypiania.remove(listaDoWypiania[0])

#funkcja do wypisywania zegarka
def printTime():
    fontForTime = pygame.font.Font(NAZWA_CZCIONKA,50)
    czas = ""
    czas = str(time.localtime(time.time()).tm_hour) + ":"
    if time.localtime(time.time()).tm_min < 10:
        czas = czas + "0" + str(time.localtime(time.time()).tm_min)
    else:
        czas = czas + str(time.localtime(time.time()).tm_min)
    czas = czas + ":"
    if time.localtime(time.time()).tm_sec < 10:
        czas = czas + "0" + str(time.localtime(time.time()).tm_sec)
    else:
        czas = czas + str(time.localtime(time.time()).tm_sec)
    timeToBlit = fontForTime.render(czas,True,(255,255,255))
    screen.blit(timeToBlit,(WIDTH - timeToBlit.get_width() - 20, 20)) #zawsze będzie w prawym górnym rogu

#wypisuje imie i nazwisko na ekranie
def printId(id,poz=0):
    fontForId = pygame.font.Font(NAZWA_CZCIONKA,120)
    idToBlit = fontForId.render(id,True,(255,255,255))
    #screen.blit(idToBlit,((WIDTH-idToBlit.get_width()) / 2, HEIGHT / 6))
    screen.blit(idToBlit,((WIDTH-idToBlit.get_width()) / 4, (HEIGHT + idToBlit.get_height()) / 6 + poz))
    #screen.blit(idToBlit,((WIDTH-idToBlit.get_width()) / 2, (HEIGHT + 2*idToBlit.get_height()) / 6 + 200))

#wypisuje pozostały czas który został do końca wyświetlania danych
#wersja z prostokątami
def printTimeLeft(timeLeft,poz=0):
    fontForTimeleft = pygame.font.Font(NAZWA_CZCIONKA,120)
    ramka = pygame.image.load("ramka.png")
    fontToBlit = fontForTimeleft.render(str(timeLeft),True,(255,255,255))
    screen.blit(ramka,(WIDTH - 200,HEIGHT / 6 + 30 + 30 + poz))
    if timeLeft > 9:
        screen.blit(fontToBlit,(WIDTH - 250 + 75,HEIGHT / 6 + 30 + poz ))
    else:
        screen.blit(fontToBlit,(WIDTH - 250 + 105,HEIGHT/ 6 + 30 + poz ))
'''
#wersja z kuleczkami
def printTimeLeft(timeLeft,poz=0):
    fontForTimeleft = pygame.font.Font(NAZWA_CZCIONKA,120)
    fontToBlit = fontForTimeleft.render(str(timeLeft),True,(102,178,255))
    pygame.draw.circle(screen,(255,255,255),(WIDTH - 120,HEIGHT / 6 + 115 + poz),80)
    if timeLeft > 9:
        screen.blit(fontToBlit,(WIDTH - 180,HEIGHT / 6 + 30 + poz ))
    else:
        screen.blit(fontToBlit,(WIDTH - 160,HEIGHT/ 6 + 30 + poz ))
'''

#funkcja sprawdzająca czy dane dziecko jest już na liście
def findOnList(newId):
    flaga = 0
    start = newId.find("- ") + 1
    if len(listaDoWypiania) > 0:
        for i in range(len(listaDoWypiania)):
            if listaDoWypiania[i].name == newId[start:len(newId)]:
                flaga = 1
    return flaga

def findOnLast7List(newId):
    flaga = 0
    global ostatnieSiedem
    for i in range(7):
        if ostatnieSiedem[i] == newId:
            flaga = 1
    return flaga

def printKolejka():
    fontForKolejka = pygame.font.Font(NAZWA_CZCIONKA,40)
    ilosc = len(listaDoWypiania) - 3
    if ilosc < 0:
        ilosc = 0
    fontToBlit = fontForKolejka.render(u"Ilość kart w kolejce: " + str(ilosc),True,(255,255,255))
    screen.blit(fontToBlit,(20,20))



#tu się zaczyna main
pygame.init()                                                       # init biblioteki do grafiki
pygame.mixer.init()                                                 # init do muzyczki
muzyczka = pygame.mixer.music.load(NAZWA_AUDIO)                     # wczytujemy muzyczke
clock = pygame.time.Clock()                                         # tworzymy zegarek
screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.FULLSCREEN) # tworzymy okno w fullscreenie
ikona = pygame.image.load(NAZWA_IKONA)                              # ładujemy ikonke
pygame.display.set_icon(ikona)                                      # i ją ustawiamy

while not done:                                                     # główna pętla, jak w AVR'ach, huh
    for event in pygame.event.get():                                # jak przyszedł jakiś event to se go obsłużymy
        if event.type == pygame.QUIT:                               # jak quit to quit
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:   #jak escape to też quit
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:        #jak 1 to tryb okienka
            screen = pygame.display.set_mode((WIDTH,HEIGHT))
        if event.type == pygame.KEYDOWN and event.key == pygame.K_2:        #jak 2 to wracamy do fullscreen
            screen = pygame.display.set_mode((WIDTH,HEIGHT),pygame.FULLSCREEN)
    screen.fill((102,178,255))                                      # wypełniamy screen ładnym kolorkiem
    printTime()                                                     # wrzucamy zegarek na ekran
    if len(listaDoWypiania) != 0:                                   # jak jest jakiś dzieciak do wypisania to wypisujemy
        listaDoWypiania[0].printMe()
        printId(listaDoWypiania[0].name) #+ " - " + str(listaDoWypiania[0].timeLeft))
        printTimeLeft(listaDoWypiania[0].timeLeft)
        if len(listaDoWypiania) > 1:
            listaDoWypiania[1].printMe()
            printId(listaDoWypiania[1].name,150) #+ " - " + str(listaDoWypiania[1].timeLeft),150)
            printTimeLeft(listaDoWypiania[1].timeLeft,150)
        if len(listaDoWypiania) > 2:
            listaDoWypiania[2].printMe()
            printId(listaDoWypiania[2].name,300) #+ " - " + str(listaDoWypiania[2].timeLeft),300)
            printTimeLeft(listaDoWypiania[2].timeLeft,300)

    getNewCard()                                                    # szukamy nowych kart
    if flagaZmianyKarty == 1:                                       # jak była to zajebiście tylko trzea dodać dzieciaka
        flagaZmianyKarty = 0                                        # zeruj flage frajerze!
        dane = getNameFromID(lastCardReaded)                        # translacja nr na nazwisko
        if dane != "":
            nowaOsoba = Person(dane)                                    # nowy obiekt klasy osoba, jak u szmuca, LOL
            if findOnList(nowaOsoba.name) == 0:                         # jeśli nie ma jeszcze na liście to WANIA DAWAJ
                listaDoWypiania.append(nowaOsoba)                       # znaczy DODAWAJ.
                ostatnieSiedem.append(lastCardReaded)
                for i in range(7):
                    ostatnieSiedem[i] = ostatnieSiedem[i+1]
                ostatnieSiedem.pop(7)
        else:
            pass                    # tutaj można dodać napis "nowa karta albo coś"
    for i in range(len(listaDoWypiania)):                           # tu se będziemy updateować stan coutdownów
        listaDoWypiania[i].update()
    cleanList()                                                     # tu se wyrzucamy z listy te które mamy timeLeft < 0
    if liczbaOstatnichTimeoutow > 10:
        screen.blit(pygame.font.Font(NAZWA_CZCIONKA,80).render(u"Brak połączenia z siecią!",True,(255,255,255)),(200,HEIGHT / 3))
    printKolejka()
    pygame.display.flip()                                           # flipaj strone (double buffering)
    clock.tick(60)                                                  # tick tock
