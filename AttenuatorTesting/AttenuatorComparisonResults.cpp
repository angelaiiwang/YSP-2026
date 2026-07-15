// Pin map (attenuator control bus, shared by all four algorithms):
//  A1 = 2
//  A2 = 3
//  A3 = 4
//  A4 = 5
//  A5 = 6
//  A6 = 7

const float V_REF = 5.0;
const float R_BITS = 10.0;
const float ADC_STEPS = (1 << int(R_BITS)) - 1;
const int potentiometerPin = A3;
const int NUM_LEVELS = 64;                 // 6-bit attenuator -> indices 0..63

const unsigned long SETTLE_MS = 5;         // settle time after switching attenuator, before reading ADC
const unsigned long CYCLE_DELAY_MS = 50;   // pacing between rounds -- tune for plotter readability

// How far the voltage has to drift from its converged value before an
// algorithm abandons its lock and searches again.
const float RECAL_DRIFT_VOLTS = 0.03;

//Voltage threshold and tolerace
const float THRESHOLD = 1.3;
const float TOLERANCE = 0.01;

// A result only gets printed once an algorithm's converged voltage is
// within this fraction of THRESHOLD (0.001 = 0.1%).
const float RESULT_PRECISION_PCT = 0.1;

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

float getVoltage() {
  int rawValue = analogRead(potentiometerPin);
  return (rawValue / ADC_STEPS) * V_REF;
}

float measureAt(int num) {
  setVoltage(toBinary(num));
  delay(SETTLE_MS);
  return getVoltage();
}

// Prints one result line if the converged voltage is within RESULT_PRECISION_PCT
// of THRESHOLD. Called once per fresh convergence event, guarded by a
// "reported" flag so it only fires the first time for that lock.
void reportIfPrecise(const char* name, float v, unsigned long startTime,
                      int steps, bool& reported) {
  if (reported) return;

  float error = abs(v - THRESHOLD);
  float errorPct = (error / THRESHOLD) * 100.0;

  if (errorPct < RESULT_PRECISION_PCT * 100.0) {
    unsigned long elapsed = millis() - startTime;
    Serial.print(name);
    Serial.print(" converged -> Time: ");
    Serial.print(elapsed);
    Serial.print(" ms, Iterations: ");
    Serial.print(steps);
    Serial.print(", Error: ");
    Serial.print(errorPct, 4);
    Serial.println(" %");
    reported = true;
  }
}

//======================= Linear search algorithm ==========================
int lin_i = 0;
bool lin_converged = false;
float lin_lastVoltage = 0;
int lin_convergedIndex = 0;
float lin_baselineVoltage = 0;

int lin_steps = 0;
unsigned long lin_startTime = 0;
bool lin_reported = false;

void resetLinear() {
  lin_i = 0;
  lin_converged = false;
  lin_lastVoltage = 0;
  lin_steps = 0;
  lin_startTime = millis();
  lin_reported = false;
}

float stepLinear() {
  if (lin_converged) {
    float v = measureAt(lin_convergedIndex);
    if (abs(v - lin_baselineVoltage) > RECAL_DRIFT_VOLTS) {
      resetLinear();
      return v;
    }
    return THRESHOLD;
  }

  float v = measureAt(lin_i);
  lin_steps++;
  lin_lastVoltage = v;
  if (v <= THRESHOLD || lin_i >= NUM_LEVELS - 1) {
    lin_converged = true;
    lin_convergedIndex = lin_i;
    lin_baselineVoltage = v;
    reportIfPrecise("Linear", v, lin_startTime, lin_steps, lin_reported);
    return THRESHOLD;
  } 
  else {
    lin_i++;
  }
  return v;
}

//======================= Binary search algorithm ==========================
int bin_left = 0;
int bin_right = NUM_LEVELS - 1;
bool bin_converged = false;
float bin_lastVoltage = 0;
int bin_convergedIndex = 0;
float bin_baselineVoltage = 0;

int bin_steps = 0;
unsigned long bin_startTime = 0;
bool bin_reported = false;

void resetBinary() {
  bin_left = 0;
  bin_right = NUM_LEVELS - 1;
  bin_converged = false;
  bin_lastVoltage = 0;
  bin_steps = 0;
  bin_startTime = millis();
  bin_reported = false;
}

float stepBinary() {
  if (bin_converged) {
    float v = measureAt(bin_convergedIndex);
    if (abs(v - bin_baselineVoltage) > RECAL_DRIFT_VOLTS) {
      resetBinary();
      return v;
    }
    return THRESHOLD;
  }

  if (bin_left >= bin_right) {
    float v = measureAt(bin_left);
    bin_steps++;
    bin_convergedIndex = bin_left;
    bin_baselineVoltage = v;
    bin_converged = true;
    reportIfPrecise("Binary", v, bin_startTime, bin_steps, bin_reported);
    return THRESHOLD;
  }

  int mid = bin_left + (bin_right - bin_left) / 2;
  float v = measureAt(mid);
  bin_steps++;
  bin_lastVoltage = v;
  if (abs(v - THRESHOLD) <= TOLERANCE) {
    bin_convergedIndex = mid;
    bin_baselineVoltage = v;
    bin_converged = true;
    reportIfPrecise("Binary", v, bin_startTime, bin_steps, bin_reported);
    return THRESHOLD;
  } 
  else if (v < THRESHOLD) {
    bin_right = mid;
  } 
  else {
    bin_left = mid + 1;
  }
  return v;
}

//===================== Interpolation search algorithm =====================
int interp_left = 0;
int interp_right = NUM_LEVELS - 1;
bool interp_converged = false;
float interp_lastVoltage = 0;
int interp_convergedIndex = 0;
float interp_baselineVoltage = 0;

int interp_steps = 0;
unsigned long interp_startTime = 0;
bool interp_reported = false;

void resetInterp() {
  interp_left = 0;
  interp_right = NUM_LEVELS - 1;
  interp_converged = false;
  interp_lastVoltage = 0;
  interp_steps = 0;
  interp_startTime = millis();
  interp_reported = false;
}

float stepInterpolation() {
  if (interp_converged) {
    float v = measureAt(interp_convergedIndex);
    if (abs(v - interp_baselineVoltage) > RECAL_DRIFT_VOLTS) {
      resetInterp();
      return v;
    }
    return THRESHOLD;
  }

  if (interp_left >= interp_right) {
    float v = measureAt(interp_left);
    interp_steps++;
    interp_convergedIndex = interp_left;
    interp_baselineVoltage = v;
    interp_converged = true;
    reportIfPrecise("Interp", v, interp_startTime, interp_steps, interp_reported);
    return THRESHOLD;
  }

  float voltLeft = measureAt(interp_left);
  interp_steps++;
  float voltRight = measureAt(interp_right);
  interp_steps++;

  if (voltRight == voltLeft) { // guard against divide-by-zero
    interp_convergedIndex = interp_left;
    interp_baselineVoltage = voltLeft;
    interp_converged = true;
    reportIfPrecise("Interp", voltLeft, interp_startTime, interp_steps, interp_reported);
    return THRESHOLD;
  }

  int pos = interp_left + (int)((THRESHOLD - voltLeft) * (interp_right - interp_left) /
                                 (voltRight - voltLeft));
  pos = constrain(pos, interp_left, interp_right);

  float v = measureAt(pos);
  interp_steps++;
  interp_lastVoltage = v;

  if (abs(v - THRESHOLD) <= TOLERANCE) {
    interp_convergedIndex = pos;
    interp_baselineVoltage = v;
    interp_converged = true;
    reportIfPrecise("Interp", v, interp_startTime, interp_steps, interp_reported);
    return THRESHOLD;
  } 
  else if (v < THRESHOLD) { 
    interp_right = pos - 1; // measured too low -> needs a LOWER index -> shrink right
  } 
  else {
    interp_left = pos + 1; // measured too high -> need a HIGHER index -> shrink left
  }
  return v;
}

//======================= Fibonacci search algorithm =======================
int fib_fm, fib_f1, fib_f2, fib_offset;
bool fib_converged = false;
bool fib_finalCheckDone = false;
float fib_lastVoltage = 0;
int fib_convergedIndex = 0;
float fib_baselineVoltage = 0;

int fib_steps = 0;
unsigned long fib_startTime = 0;
bool fib_reported = false;

void fibNumSetup(int input) {
  int numbers[] = {0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89};
  int arraySize = sizeof(numbers) / sizeof(numbers[0]);
  for (int i = 0; i < arraySize; i++) {
    if (numbers[i] >= input) {
      fib_fm = numbers[i];
      fib_f1 = numbers[i - 1];
      fib_f2 = numbers[i - 2];
      break;
    }
  }
}

void resetFib() {
  fibNumSetup(NUM_LEVELS);
  fib_offset = -1;
  fib_converged = false;
  fib_finalCheckDone = false;
  fib_lastVoltage = 0;
  fib_steps = 0;
  fib_startTime = millis();
  fib_reported = false;
}

float stepFibonacci() {
  if (fib_converged) {
    float v = measureAt(fib_convergedIndex);
    if (abs(v - fib_baselineVoltage) > RECAL_DRIFT_VOLTS) {
      resetFib();
      return v;
    }
    return THRESHOLD;
  }

  if (fib_f2 > 0) {
    int index = min(fib_offset + fib_f2, NUM_LEVELS - 1);
    float v = measureAt(index);
    fib_steps++;
    fib_lastVoltage = v;
    if (abs(v - THRESHOLD) <= TOLERANCE) {
      fib_convergedIndex = index;
      fib_baselineVoltage = v;
      fib_converged = true;
      reportIfPrecise("Fib", v, fib_startTime, fib_steps, fib_reported);
      return THRESHOLD;
    } 
    else if (v < THRESHOLD) {
      // measured too low -> need a LOWER index -> move left: shrink from
      // the top, keep the same offset, don't advance past this index
      int newF1 = fib_f1 - fib_f2;
      int newF2 = fib_f2 - newF1;
      fib_f1 = newF1;
      fib_f2 = newF2;
    } 
    else {
      // measured too high -> need a HIGHER index -> move right: discard
      // everything up to and including this index, advance offset
      int newF1 = fib_f2;
      int newF2 = fib_f1 - fib_f2;
      fib_f1 = newF1;
      fib_f2 = newF2;
      fib_offset = index;
    }
  } 
  else if (!fib_finalCheckDone) {
    fib_finalCheckDone = true;
    int lastIndex = fib_offset + 1;
    float v = fib_lastVoltage;
    if (lastIndex < NUM_LEVELS) {
      v = measureAt(lastIndex);
      fib_steps++;
      fib_lastVoltage = v;
    }
    fib_convergedIndex = (lastIndex < NUM_LEVELS) ? lastIndex : fib_offset;
    fib_baselineVoltage = v;
    fib_converged = true;
    reportIfPrecise("Fib", v, fib_startTime, fib_steps, fib_reported);
    return THRESHOLD;
  }
  return fib_lastVoltage;
}

void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  Serial.begin(9600);
  resetLinear();
  resetBinary();
  resetInterp();
  resetFib();
}

void loop() {
  // Each stepX() call advances that algorithm's search by one measurement.
  // A result line prints automatically (via reportIfPrecise) the moment an
  // algorithm's converged voltage lands within RESULT_PRECISION_PCT of
  // THRESHOLD -- nothing else is printed every loop.
  stepLinear();
  stepBinary();
  stepInterpolation();
  stepFibonacci();

  delay(CYCLE_DELAY_MS);
}
