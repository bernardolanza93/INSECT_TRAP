/*
Simple Deep Sleep with Timer Wake Up
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories

This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots

This code is under Public Domain License.

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
*/

#define uS_TO_S_FACTOR 1000000ULL  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  60      /* Time ESP32 will go to sleep (in seconds) */
#define RELAY 17
#define PIN_IN_RP 16

RTC_DATA_ATTR int bootCount = 0;

int val = 0;

/*
Method to print the reason by which ESP32
has been awaken from sleep
*/
void print_wakeup_reason(){
  esp_sleep_wakeup_cause_t wakeup_reason;

  wakeup_reason = esp_sleep_get_wakeup_cause();

  switch(wakeup_reason)
  {
    case ESP_SLEEP_WAKEUP_EXT0 : Serial.println("Wakeup caused by external signal using RTC_IO"); break;
    case ESP_SLEEP_WAKEUP_EXT1 : Serial.println("Wakeup caused by external signal using RTC_CNTL"); break;
    case ESP_SLEEP_WAKEUP_TIMER : Serial.println("Wakeup caused by timer"); break;
    case ESP_SLEEP_WAKEUP_TOUCHPAD : Serial.println("Wakeup caused by touchpad"); break;
    case ESP_SLEEP_WAKEUP_ULP : Serial.println("Wakeup caused by ULP program"); break;
    default : Serial.printf("Wakeup was not caused by deep sleep: %d\n",wakeup_reason); break;
  }
}

void setup(){
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  //Increment boot number and print it every reboot
  ++bootCount;
  pinMode(PIN_IN_RP, INPUT);  
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, HIGH); // raspi spenta
  


  //Print the wakeup reason for ESP32
  print_wakeup_reason();

  /*
  First we configure the wake up source
  We set our ESP32 to wake up every 5 seconds
  */
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);


  /*
  Next we decide what all peripherals to shut down/keep on
  By default, ESP32 will automatically power down the peripherals
  not needed by the wakeup source, but if you want to be a poweruser
  this is for you. Read in detail at the API docs
  http://esp-idf.readthedocs.io/en/latest/api-reference/system/deep_sleep.html
  Left the line commented as an example of how to configure peripherals.
  The line below turns off all RTC peripherals in deep sleep.
  */
  //esp_deep_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  //Serial.println("Configured all RTC Peripherals to be powered down in sleep");

  /*
  Now that we have setup a wake cause and if needed setup the
  peripherals state in deep sleep, we can now start going to
  deep sleep.
  In the case that no wake up sources were provided but deep
  sleep was started, it will sleep forever unless hardware
  reset occurs.
  */
  
}

void loop(){
  //Serial.println("start loop");

  long int t_start = millis()/1000;
  digitalWrite(RELAY, LOW); //raspi spenta
  Serial.println("ralay off");
  
  


  digitalWrite(RELAY, HIGH); // accendo raspi
  Serial.println("ralay on");
  delay(1000); // Waits for 1 second

  
  //val = digitalRead(PIN_IN_RP); 
  int i = 0;
  while (i < 60){
    delay(500);
    val = digitalRead(PIN_IN_RP);   
    Serial.print("rval of input pin:");
    Serial.println(val);
    i++;
    if (val == 1) {
      delay(500);
      Serial.println("input recived from raspi, shut down raspi and going to sleep");
      digitalWrite(RELAY, LOW); // spengo raspi 
      delay(1000); // Waits for 1 second
      break;
      
      
    }
    else {
      Serial.println("NO data incoming, wait");
      delay(1000);
    }
  }
  //spengo comunque la raspi se sono passati piu di 10 cicli da 2.5 s
  digitalWrite(RELAY, LOW); // spengo raspi 
  

  delay(500);
  long int t_end = millis()/1000;
  long int t_tot = t_end - t_start; //second passed
  long int total_time_to_wait = (24*60*60) - t_tot;
  Serial.print("total execution time : ");
  Serial.println(t_tot);

  
  
  esp_deep_sleep_start();
  delay(500);
}
