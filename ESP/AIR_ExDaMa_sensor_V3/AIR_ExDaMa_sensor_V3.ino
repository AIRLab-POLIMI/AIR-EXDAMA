#include <WiFi.h>//wifi library for esp
#include <WiFiUDP.h>//udp library for udp
#include <stdlib.h>
#include <EEPROM.h>//to access the eeprom



#define DEFAULT_SENSOR_VALUE_REDUCTION_FOR_PRESSION 4//default parameter values for the automatic calibration
#define DEFAULT_SENSOR_VALUE_REDUCTION_FOR_RELEASE 2
#define CAL_BATCHES_SAMPLES 20 //number of samples on which the mode is computed when removing environmental noise
#define CAL_BATCHES 5//number of bathes on which the mode is averaged when removing environmental noise
#define N_SENSORS 7//maximum number of allowed sensors
#define SENSOR_ID 6//ID of the particular sensor, this value has to be changed for every sensor
#define RED_PIN 12//pin numbers for the LED
#define GREEN_PIN 14
#define BLUE_PIN 27
#define RED_VALUE 148// LED color 
#define GREEN_VALUE 0
#define BLUE_VALUE 211
#define CAPACITY_PIN T8
#define CALIBRATION_DELAY 4000 //Time the user has to move away from the sensor after it receive a recalibration command



void send(int x);//send a value to the server(raspberry)
void calibrate(int press_red, int release_red);//calibrate automatically using the given parameters
//void sensor_malfunction();//not used


IPAddress staticIP(192,168,4,10+SENSOR_ID);//esp32 IP, the first numbers are the same as the gateway(raspberry), the last number has to be SENSOR_ID+10 to make communication easier
IPAddress gateway(192,168,4,1);//raspberry's IP
IPAddress subnet(255,255,255,0);//subnet mask
WiFiUDP Udp;
IPAddress server(192,168,4,1);

byte ledPin = 2; //pin used to command the led
char ssid[] = "Thesis";           // SSID of the network
char passw[] = "aereolabio";         // password of the network
int UDPPort=2390; //port used for the communication
uint16_t press_t;//Set the press treshold for touch detection
uint16_t release_t;//set the release treshold for touch detection 
uint8_t *input_data;//Used to read data coming from the raspberry
int outlier_filter=0;// Filter out the first value under treshold to remove the "outlier noise" of the sensor
int instability_filter=0;//Filer out the first value above the release treshold
int flag=0;//check if the sensors is in the "pressed" status
uint8_t calibration_type;//to distinguish between automatic and manual calibration

 
 

void setup() {
  uint8_t press_red;//Contain the parameter to calibrate automatically
  uint8_t release_red;
  //Serial.begin(115200);//low baud rate interfere with the libraries
  
  pinMode(ledPin, OUTPUT);//configure the built-in led

  WiFi.mode(WIFI_STA);//set the correct operating mode for the esp
  WiFi.begin(ssid, passw);// connects to the WiFi network
  WiFi.config(staticIP, gateway, subnet, gateway);//force the static IP. the 4th parameter is necessary to avoid this function to get bugged

  ledcAttachPin(RED_PIN, 1); // assign RGB led pins to channels
  ledcAttachPin(GREEN_PIN, 2);
  ledcAttachPin(BLUE_PIN, 3);
  
  // Initialize channels 
  // channels 0-15, resolution 1-16 bits, freq limits depend on resolution
  // ledcSetup(uint8_t channel, uint32_t freq, uint8_t resolution_bits);
  ledcSetup(1, 12000, 8); // 12 kHz PWM, 8-bit resolution
  ledcSetup(2, 12000, 8);
  ledcSetup(3, 12000, 8);

  ledcWrite(1, RED_VALUE);//Turn on the LED
  ledcWrite(2, GREEN_VALUE);
  ledcWrite(3, BLUE_VALUE);

  
  while (WiFi.status() != WL_CONNECTED)//stop the code while waiting for the esp to connect
    {delay(500);}

 delay(500);

  EEPROM.begin(512);//retrieve the treshold parameters from the eeprom and interpret them based on the byte stored in position 4, that set the calibration type
  calibration_type=EEPROM.read(4);
  
  if (calibration_type==1)//if set to 1 it uses absolute calibration values (not recommended unless the automatic calibration is not working properly)
  {press_t=EEPROM.read(0);
   press_t<<=8;
   press_t+=EEPROM.read(1);
   release_t=EEPROM.read(2);
   release_t<<=8;
   release_t+=EEPROM.read(3);}
  else if (calibration_type==2)// if set to 2 it uses an environmental calibration with user defined reduction values. This should be the standard operating mode since it's the most robust one)
  {press_red=EEPROM.read(5);
   press_red<<=8;
   press_red+=EEPROM.read(6);
   release_red=EEPROM.read(7);
   release_red<<=8;
   release_red+=EEPROM.read(8);
   calibrate(press_red, release_red);}
  else // if it's set to 0 or any other value (either used defined or due to being a new sensor) it uses the environment based calibration with predefined reduction values
   {calibration_type=2;
    calibrate(DEFAULT_SENSOR_VALUE_REDUCTION_FOR_PRESSION, DEFAULT_SENSOR_VALUE_REDUCTION_FOR_RELEASE);}


  Udp.begin(UDPPort);//start the udp communication
  delay(2000);
  ledcWrite(1, 0);//Turn of the LED
  ledcWrite(2, 0);
  ledcWrite(3, 0);
  delay(1000);
}

void loop() {
    unsigned long value =  touchRead(CAPACITY_PIN);//start measuring the capacitance
    int input_size;//to store the size of the input data received from the raspberry
    int i;//counter

if(input_size=Udp.parsePacket())//if data from the raspberry is received, it is read. the data is encoded as 2 16 bit integers, first high treshold then low treshold
{  
   ledcWrite(1, RED_VALUE);
   ledcWrite(2, GREEN_VALUE);
   ledcWrite(3, BLUE_VALUE);
   input_data= (uint8_t *)malloc(input_size * sizeof (uint8_t));
   Udp.read(input_data, input_size);
   if (input_data[0]==0 || input_data[0]==1)//If the RPi command is set to 0 or 1, the ESP update ir's calibration parameters in absolute mode
      {calibration_type=1;
      press_t=input_data[1];
      press_t<<=8;
      press_t+=input_data[2];
      release_t=input_data[3];
      release_t<<=8;
      release_t=input_data[4];
      if (input_data[0]==1)//if the command was set to "save" it also saves the new values on the eeprom
          {EEPROM.write(4,1);
          for (i=0; i<4; i++)
              {EEPROM.write(i,input_data[i+1]);}
          EEPROM.commit();}
      }
   else if(input_data[0]==2)//if the command is set to diagnostic the sensor will start sending the sensor's readings until reset
      {while(1)
          {if (value>=0 and value<253)//Send data normally
              {send(value);}
          else if(value==-1)//If error -1, send 253
              {send(253);}
          else if (value==-2)//if error -2, send 254
              {send(254);}
          else
              {send(255);}//anythithing else, send 255
          value=touchRead(CAPACITY_PIN);}
      }
   else if (input_data[0]==3 || input_data[0]==4)//if the RPi request is a 3 or 4, it update the calibration parameters in automatic mode
      {delay(CALIBRATION_DELAY);
      calibration_type=2;
      press_t=input_data[1];
      press_t<<=8;
      press_t+=input_data[2];
      release_t=input_data[3];
      release_t<<=8;
      release_t=input_data[4];
      calibrate(press_t, release_t);
          if (input_data[0]==4)//if the command was set to "save" it saves the new values on the eeprom
            {EEPROM.write(4,2);
             for (i=5; i<9; i++)
                {EEPROM.write(i,input_data[i-4]);}
             EEPROM.commit();
          }
      }
   else if (input_data[0]==5)// if the command code is 5, the ESP performs a recalibration (only valid for automatic mode)
      {delay(CALIBRATION_DELAY);
       value=EEPROM.read(4);
          if (value==2)//if the calibration type is set to 2 then user defined reduction values are used
              {press_t=EEPROM.read(5);
               press_t<<=8;
               press_t+=EEPROM.read(6);
               release_t=EEPROM.read(7);
               release_t<<=8;
               release_t+=EEPROM.read(8);
               calibrate(press_t, release_t);}
          else if (value!=1)//if the calibration type is set to any value diferent for 1 (manual calibration mode) then default reduction values are used
               {calibrate(DEFAULT_SENSOR_VALUE_REDUCTION_FOR_PRESSION, DEFAULT_SENSOR_VALUE_REDUCTION_FOR_RELEASE);}
      }// if the calibration is set to other values nothing will happen
   
   
   free(input_data);
   delay(2000);
   ledcWrite(1, 0);
   ledcWrite(2, 0);
   ledcWrite(3, 0);
   }
 
if (value<=press_t)//if the capacity value is under a certain treshold and no flag is raised, send sensor id to the raspberry. this communicates that the sensor has been pressed. it raise a flag
    {if (outlier_filter==0)//discard the first value regarded as "press"
        {outlier_filter=1;}
    else//if the press value has already been discarded, activate the "press" status
        {if (flag==0)
            {ledcWrite(1, RED_VALUE);
             ledcWrite(2, GREEN_VALUE);
             ledcWrite(3, BLUE_VALUE);
             flag=1;
             send(SENSOR_ID);}
         if (instability_filter==1)//reset the filter
             {instability_filter=0;}
        }
    }
else if (value>=release_t && flag==1)//if i get a value under a second treshold it send a message to the raspberry equal to the sensor id + the maximum nuber of supported sensors
    {if (instability_filter==0) //if it's the first value above the release "treshold", ignore it
        {instability_filter=1;}
    else//if the first release value has already been discarded, activate the "release" status
        {flag=0;//this tells the pi that the sensor has been released. the flag is put down
         send(SENSOR_ID+N_SENSORS);
         ledcWrite(1, 0);
         ledcWrite(2, 0);
         ledcWrite(3, 0);
         outlier_filter=0;
         if (outlier_filter==1)//reset the filter
            {outlier_filter=0;}
        }
    }
}


/*
void sensor_malfunction()//not used
{while(1)
{ledcWrite(1, RED_VALUE);
  ledcWrite(2, GREEN_VALUE);
  ledcWrite(3, BLUE_VALUE);
  delay(1000);
  ledcWrite(1, 0);
  ledcWrite(2, 0);
  ledcWrite(3, 0);
  delay(1000);}}
*/

void calibrate (int press_red, int release_red)//the passed variables are the values to be subctracted from the ambient value to obtain the press treshold and the release treshold
{ int x,x2,x3,x4;
  int cal_max_mode_index;
  int cal_flag;
  unsigned long cal_batch[CAL_BATCHES_SAMPLES][2];
  unsigned long capacity;
  int even_modes_counter;
  float batch_mode;
  int cumulative_mode=0;
  
  for (x=0; x<10; x++)// execute some random reading waiting for the reading to stabilize (it has been found that the initial values after starting this function are likely wrong)
  {touchRead(CAPACITY_PIN);}
  
  for (x=0; x<CAL_BATCHES; x++)//average the result of a number of batches CAL_BATCHES
  {
   x4=0;
   for(x2=0; x2<CAL_BATCHES_SAMPLES; x2++)//extract the mode of a batch, if more values have the same mode, it is averaged between them
     {capacity=touchRead(CAPACITY_PIN);
      cal_flag=0;
      
     if (x4==0)  //add to a sequence of tracked lenght the measured value if new or increase an old value counter if repeated
      {cal_batch[x4][0]=capacity;
       cal_batch[x4][1]=1;
       x4++;
       flag=1;}
     else
      {for (x3=0; x3<x4; x3++)
       {if (cal_batch[x3][0]==capacity)
        {cal_batch[x3][1]++;
         cal_flag=1;
         break;}}}
     if (cal_flag==0)
      {cal_batch[x4][0]=capacity;
       cal_batch[x4][1]=1;
       x4++;}}
       
   cal_max_mode_index=0;
   for (x2=1; x2<x4; x2++)//obtain the list index referring to the mode
    {if (cal_batch[x2][1]>cal_batch[cal_max_mode_index][1])
      {cal_max_mode_index=x2;}}
      
   batch_mode=0;
   even_modes_counter=0;
   for (x2=0; x2<x4; x2++)//if more modes are present, the final result is their average
    {if (cal_batch[cal_max_mode_index][1]==cal_batch[x2][1])
      {batch_mode+=float(cal_batch[x2][0]);
       even_modes_counter++;}}
   batch_mode/=even_modes_counter;
   cumulative_mode+=batch_mode;}//sum the mode of every batch

   
   cumulative_mode/=CAL_BATCHES;//divide the cumulative mode by the batches, thus averaging it
   press_t=uint16_t(floor(cumulative_mode))-press_red;//after obtaining the average batch mode it compute the tresholds by removing the user defined amounts for them
   release_t=uint16_t(floor(cumulative_mode))-release_red;//approaching this way makes it so that is possible to calibrate without having the user touch the sensor in most situations
  }


void send(int x)//send an integer to the raspberry
{
char val[7];         //the string representing the message number will be stored in this char array
Udp.beginPacket(server, UDPPort);     //prepare the packet
//itoa(x,val,10); //(integer, yourBuffer, base), convert int to string
  Udp.write(uint8_t(x));//create the packet
  Udp.endPacket(); //send the packet
}
