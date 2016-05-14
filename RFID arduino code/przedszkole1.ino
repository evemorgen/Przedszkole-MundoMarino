#include <SPI.h>
#include <MFRC522.h>
#include <String.h>
#include <EtherCard.h>

#define SS_RFID_PIN 6
#define RST_RFID_PIN 5
#define LED_B 16
#define LED_G 15
#define LED_R 14

MFRC522 czytnik(SS_RFID_PIN,RST_RFID_PIN);
MFRC522::MIFARE_Key key;

int odczytaneID[10][5];
int iloOdczytKart = 0;
boolean flaga = 0;
int ileCzeka = 0;

static byte mymac[] = { 0x74,0x69,0x69,0x2D,0x30,0x31 };
static byte myip[] = { 192,168,1,203 };

byte Ethernet::buffer[500];
BufferFiller bfill;


int changeUID()
{
  led(LED_R,0);
  led(LED_G,0);
  for (byte i = 0; i < 6; i++)
    key.keyByte[i] = 0xFF;
  while(1)
  {
    if(czytnik.PICC_IsNewCardPresent()) {czytnik.PICC_ReadCardSerial(); break;}
    led(LED_B,1);
    delay(500);
    led(LED_B,0);
    delay(500);

  }
  Serial.println("Writing new ID, begins now.");
  byte newUid[] = {random(255),random(255),random(255),random(255)};
  Serial.print("New UID: ");
  for(int i = 0;i<4;i++)
    Serial.print(String(newUid[i]) + ".");
  Serial.println();
  if ( czytnik.MIFARE_SetUid(newUid, (byte)4, true) )
            Serial.println(F("Wrote new UID to card."));
  led(LED_B,0);

}

static word homePage() {
  long t = millis() / 1000;
  word h = t / 3600;
  byte m = (t / 60) % 60;
  byte s = t % 60;
  bfill = ether.tcpOffset();
  bfill.emit_p(PSTR(
    "HTTP/1.0 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Pragma: no-cache\r\n"
    "\r\n"
    "<meta http-equiv='refresh' content='1'/>"
    "<title>Awesome RFID serverr</title>" 
    "<h2>Time I'm working fine - $D$D:$D$D:$D$D</h2>"
    "<h3>How many cards readed? - $D</h3>"
    "<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    //"<h1>Card $D - $D.$D.$D.$D</h1>"
    ),
    h/10, h%10, m/10, m%10, s/10, s%10,
    iloOdczytKart,
    odczytaneID[0][4], odczytaneID[0][0], odczytaneID[0][1], odczytaneID[0][2], odczytaneID[0][3]
    //odczytaneID[1][4], odczytaneID[1][0], odczytaneID[1][1], odczytaneID[1][2], odczytaneID[1][3],
    //odczytaneID[2][4], odczytaneID[2][0], odczytaneID[2][1], odczytaneID[2][2], odczytaneID[2][3],
    //odczytaneID[3][4], odczytaneID[3][0], odczytaneID[3][1], odczytaneID[3][2], odczytaneID[3][3],
    //odczytaneID[4][4], odczytaneID[4][0], odczytaneID[4][1], odczytaneID[4][2], odczytaneID[4][3],
    //odczytaneID[5][4], odczytaneID[5][0], odczytaneID[5][1], odczytaneID[5][2], odczytaneID[5][3],
    //odczytaneID[6][4], odczytaneID[6][0], odczytaneID[6][1], odczytaneID[6][2], odczytaneID[6][3],
    //odczytaneID[7][4], odczytaneID[7][0], odczytaneID[7][1], odczytaneID[7][2], odczytaneID[7][3]
    //odczytaneID[8][4], odczytaneID[8][0], odczytaneID[8][1], odczytaneID[8][2], odczytaneID[8][3],
    //odczytaneID[9][4], odczytaneID[9][0], odczytaneID[9][1], odczytaneID[9][2], odczytaneID[9][3]
     );
  return bfill.position();
}


void led(int nr, int onOff)
  {
    if(onOff) digitalWrite(nr,LOW);
    else      digitalWrite(nr,HIGH);
  }
  
  
void ledInit()
{
 pinMode(LED_R,OUTPUT);
 pinMode(LED_G,OUTPUT);
 pinMode(LED_B,OUTPUT);
 
 digitalWrite(LED_R,HIGH);
 digitalWrite(LED_G,HIGH);
 digitalWrite(LED_B,HIGH);
}

void buttonInit()
{
  pinMode(2,INPUT);
  digitalWrite(2,HIGH);
}

boolean ifButton()
{
  return !digitalRead(2);
}

void moveTable(byte noweWart[], int nr)
{
  for(int i = 8;i>-1;i--)
    {
      odczytaneID[i+1][0] = odczytaneID[i][0];
      odczytaneID[i+1][1] = odczytaneID[i][1];
      odczytaneID[i+1][2] = odczytaneID[i][2];
      odczytaneID[i+1][3] = odczytaneID[i][3];
      odczytaneID[i+1][4] = odczytaneID[i][4];
    }
  odczytaneID[0][0] = noweWart[0];
  odczytaneID[0][1] = noweWart[1];
  odczytaneID[0][2] = noweWart[2];
  odczytaneID[0][3] = noweWart[3];
  odczytaneID[0][4] = nr;

}

void setup()
{
 ledInit();
 
 Serial.begin(57600);
 if (ether.begin(sizeof Ethernet::buffer, mymac) == 0)
    Serial.println( "Failed to access Ethernet controller"); 
 ether.staticSetup(myip);
 SPI.begin();
 czytnik.PCD_Init();
 
 buttonInit();
  
 for(int i = 0;i<10;i++)
   { 
     odczytaneID[i][0] = 0;
     odczytaneID[i][1] = 0;
     odczytaneID[i][2] = 0;
     odczytaneID[i][3] = 0;
     odczytaneID[i][4] = 0;
   }
 
 for(int i = 0;i<3;i++)
 {
   led(LED_R,1);
   delay(300);
   led(LED_R,0);
   delay(300);
 }
 
}



void loop()
{
 
  for(int i = 0;i<60;i++)
    {
         word len = ether.packetReceive();
         word pos = ether.packetLoop(len);
         if (pos)  // check if valid tcp data is received
           ether.httpServerReply(homePage()); // send web page data 
         delay(50);
         led(LED_R,1);
         led(LED_G,0);
    }
  
  while(1)
     {
       if(czytnik.PICC_IsNewCardPresent()) 
       {
         czytnik.PICC_ReadCardSerial();
            moveTable(czytnik.uid.uidByte, iloOdczytKart+1);
         break;
       }
       word len = ether.packetReceive();
       word pos = ether.packetLoop(len);
       //if(ifButton()) changeUID();
       if (pos)  // check if valid tcp data is received
         ether.httpServerReply(homePage()); // send web page data  
        led(LED_R,0);
        led(LED_G,1);
      delay(50);
     }
       led(LED_R,1);
       led(LED_G,0);
   iloOdczytKart++;
   
   for(int i = 0;i<10;i++)
     {
       for(int j = 0;j<5;j++)
         Serial.print(odczytaneID[i][j]);
       Serial.println();
     } 

}
