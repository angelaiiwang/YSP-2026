/*
A1 = 2
A2 = 3
A3 = 4
A4 = 5
A5 = 6
A6 = 7
*/

const float V_REF = 5.0;     // Analog reference voltage (e.g., 5V or 3.3V)
const float R_BITS = 10.0;   // ADC resolution (bits)
const float ADC_STEPS = (1 << int(R_BITS)) - 1;
const int potentiometerPin = A3;
const float threshold = 1.3; 

float getVoltage() {
  int rawValue = analogRead(potentiometerPin); // Read the analog input
  float voltage = (rawValue / ADC_STEPS) * V_REF; // Convert to voltage
  Serial.print("Voltage: ");
  Serial.print(voltage, 3); // Print voltage with 3 decimal places
  Serial.print(" V");
  for (int i = 2; i < 8; i++) {
    Serial.print(digitalRead(i));
  }
  Serial.println();
  Serial.println("++++++++++++++++++++++++");

  return voltage; 
}

bool check (float voltage)
{
  if (voltage <= threshold)
  {
    return true; 
  }

  return false; 
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  Serial.begin(9600); // Initialize serial communication
  Serial.println(ADC_STEPS);  
}

void loop() {
  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);

  float voltage = 0; 

  for (int i = 0; i < 64; i++) 
  {
    Serial.print("Attenuation: ");
    int num = 64 - i;
    Serial.println(num);
    String bin = String(i, BIN);
    int len = bin.length();
    int add = 6 - len;
    String binary = "";
    for (int z = 0; z < add; z++) {
      binary += "0";
    }
    binary += bin;
    Serial.println(binary);
    for (int j = 0; j < 6; j++) {
      if (binary[j] == '0') {
        digitalWrite(j+2, LOW);
      }
    }

    voltage = getVoltage();
    bool cont = check(voltage); 

    if (cont)
    {
      break; 
    }

    delay(200);

    digitalWrite(2, HIGH);
    digitalWrite(3, HIGH);
    digitalWrite(4, HIGH);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
  }
}
