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
const float threshold = 1.4; //Required voltage threshold
float tolerance = 0.01; //Tolerance for the algorithm closeness
bool finished = 0;  //Final check for the algorithm completion

//Minimum and Maximum voltage values from attenuation
float minVoltage;
float maxVoltage;
int pos;

float oldVoltage;
float newVoltage;

//Method returns the voltage recorded by analog pin
float getVoltage() {
  int rawValue = analogRead(potentiometerPin); // Read the analog input
  float voltage = (rawValue / ADC_STEPS) * V_REF; // Convert to voltage
  newVoltage = voltage;
  return(voltage);
}

//Method writes the voltage of the MINIMUM, MAXIMUM and OUTPUT voltages
void writeVoltage() {
  Serial.print("Min:");
  Serial.print(measureAt(63));
  Serial.print("\t");

  Serial.print("Max:");
  Serial.print(measureAt(0));
  Serial.print("\t");

  Serial.print("Output:");
  Serial.print(measureAt(pos), 3); // Print voltage with 3 decimal places
  Serial.println();
}

//Method returns the binary string of a integer input
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

//Method sets the attenuator to produce new voltage output
void setVoltage(String bin) {
  for (int i = 0; i < 6; i++) {
    digitalWrite(i + 2, bin[i] == '1' ? HIGH : LOW);
  }
}

bool checkVoltageChange() {
  if (abs(oldVoltage - newVoltage) <= (tolerance * 2)) {
    return false;
  }
  else {
    oldVoltage = newVoltage;
    return true;
  }
}

//Returns the voltage at the number after setting the 
//attenuator to produce new voltage output
float measureAt(int num) {
  setVoltage(toBinary(num));
  return getVoltage();
}

//Interpolation search algorithm
int interpolationSearch(int left, int right) {

  while (left < right) {
    pos = left + (threshold - measureAt(left)) * (right - left) / 
          (measureAt(right)- measureAt(left));
    if (abs(measureAt(pos) - threshold) <= tolerance) {
      finished = 1;
      writeVoltage();
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
  // minVoltage = measureAt(0);
  // maxVoltage = measureAt(63); 
}

void loop() {
  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);
  //delay(5000);
  interpolationSearch(0, 63); 
  writeVoltage();
  while (finished){
    delay(1000);
    writeVoltage();
    if (checkVoltageChange()) {
      finished = 0;
    }
  }
}
