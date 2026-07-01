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
int newStart = 0;
float tolerance = 0.01;
bool finished = 0;

float getVoltage() {
  int rawValue = analogRead(potentiometerPin); // Read the analog input
  float voltage = (rawValue / ADC_STEPS) * V_REF; // Convert to voltage
  return(voltage);
}

void writeVoltage() {
  Serial.print("Voltage: ");
  Serial.print(getVoltage(), 3); // Print voltage with 3 decimal places
  Serial.print(" V");
  for (int i = 2; i < 8; i++) {
    Serial.print(digitalRead(i));
  }
  Serial.println();
  Serial.println("++++++++++++++++++++++++");
}

String toBinary(int num) {
  String bin = String(num, BIN);
  int len = bin.length();
  int add = 6 - len;
  String binary = "";
  for (int z = 0; z < add; z++) {
    binary += "0";
  }
  binary += bin;
  return binary;
}

void setVoltage(String bin) {
  for (int i = 0; i < 6; i++) {
    digitalWrite(i + 2, bin[i] == '1' ? HIGH : LOW);
  }
}

float measureAt(int num) {
  setVoltage(toBinary(num));
  return getVoltage();
}

int interpolationSearch(int left, int right) {
  int pos;

  while (left < right) {
    pos = left + (threshold - measureAt(left)) * (right - left) / 
          (measureAt(right)- measureAt(left));
    if (abs(measureAt(pos) - threshold) <= tolerance) {
      finished = 1;
      return pos;
    }
    else if (measureAt(pos) < threshold) {
      left = pos + 1;
    }
    else {
      right = pos - 1;
    }
    writeVoltage();
  }
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  Serial.begin(9600);
  Serial.println(ADC_STEPS);  
}

void loop() {
  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);
  interpolationSearch(0, 63); 
  writeVoltage();
  while (finished){
    delay(1000);
  }
}
