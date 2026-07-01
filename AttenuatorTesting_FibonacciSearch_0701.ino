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
const float threshold = 1.4; 
const float tolerance = 0.1;
// fibonacci num ref values 
int fm; 
int f1; 
int f2; 

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

void setVoltage(String bin) {
  for (int i = 0; i < 6; i++) {
    digitalWrite(i + 2, bin[i] == '1' ? HIGH : LOW);
  }
}

// convert base 10 number to binary string 
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

// returns smallest fibonacci number greater than or equal to a num
void fibNumSetup(int input) {

    int numbers[] = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89};
    int arraySize = sizeof(numbers) / sizeof(numbers[0]);
    
    for (int i = 0; i < arraySize; i++) {
        if (numbers[i] >= input) {
            fm = numbers[i]; 
            f1 = numbers[i-1]; 
            f2 = numbers[i-2];
            break;
        }
    }
}

int fibonacciSearch(int length) {
    fibNumSetup(length);
    int offset = -1; 
    int left = 0;
    int right = length - 1;
    
    while (f2 > 0) {
        int index = min(offset + f2, length - 1);
        setVoltage(toBinary(index)); 
        writeVoltage(); 
        float measured = getVoltage(); 
        
        if (abs(measured - threshold) <= tolerance) {
            return index; 
        } else if (measured < threshold) {
            // move right 
            f1 = f1 - f2;
            f2 = f2 - f1;
            offset = index;
        } else {
            // move left 
            f1 = f2;
            f2 = f1 - f2;
        }
    }
    
    int lastIndex = offset + 1;
    if (lastIndex < length) {
        setVoltage(toBinary(lastIndex));
        writeVoltage();
        float measured = getVoltage();
        if (abs(measured - threshold) <= tolerance) {
            return lastIndex;
        }
    }
    
    return -1;
}

void loop() {
    for (int i = 2; i < 8; i++) {
        digitalWrite(i, LOW);
    }
    
    int result = fibonacciSearch(64); 
    
    if (result != -1) {
        Serial.print("Found at index: ");
        Serial.println(result);
        Serial.print("Binary value: ");
        Serial.println(toBinary(result));
    } else {
        Serial.println("Value not found within tolerance");
    }
    
    delay(2000); 
}