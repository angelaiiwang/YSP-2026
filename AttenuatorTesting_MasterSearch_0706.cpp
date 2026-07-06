/*
 * Combined Threshold-Voltage Search Visualizer
 * ---------------------------------------------
 * Runs Linear, Binary, Interpolation, and Fibonacci searches side-by-side
 * on ONE shared attenuator (pins 2-7) and ONE shared voltage sense pin (A3).
 *
 * They can't physically run "at once" (only one attenuator setting exists
 * at any instant), but each algorithm gets exactly one turn per pass
 * through loop(): set its chosen attenuation, settle, measure, advance its
 * own search state. Because all four take their turn within the same
 * pass, every trace updates together each cycle -- so on the Serial
 * Plotter they appear to converge in sync, in real time.
 *
 * RECALIBRATION (like the original interpolation file's checkVoltageChange):
 * once an algorithm converges, it keeps re-measuring at its locked-in index
 * every pass. If that reading drifts away from its value at convergence by
 * more than RECAL_DRIFT_VOLTS, that algorithm resets and searches again
 * from scratch -- all four independently.
 *
 * v4 fixes vs v3:
 * - Interpolation: reverted to recomputing measureAt(left)/measureAt(right)
 *   every iteration, matching the original file exactly (removed the
 *   endpoint-caching optimization). Kept a constrain() on pos as a safety
 *   net against out-of-range attenuator indices, which the original lacked.
 * - Fibonacci: fixed a real bug present in the original file. Both update
 *   branches reused a variable AFTER it had already been overwritten on the
 *   previous line, which broke the Fibonacci-triple invariant (f2 could
 *   collapse to 0 and end the search early). Rewritten with temp variables
 *   so f1/f2 always remain genuine consecutive Fibonacci numbers.
 *
 * v5 fixes vs v4:
 * - Both Interpolation and Fibonacci had their search direction backwards
 *   relative to Binary search's (correct) convention. On this hardware,
 *   voltage decreases as attenuator index increases. Binary correctly
 *   narrows toward LOWER indices when the reading is too low; Interpolation
 *   and Fibonacci were narrowing toward HIGHER indices instead, which
 *   pushed them away from the threshold rather than toward it. Both are now
 *   flipped to match Binary's direction.
 *
 * Pin map (attenuator control bus, shared by all four algorithms):
 * A1 = 2
 * A2 = 3
 * A3 = 4
 * A4 = 5
 * A5 = 6
 * A6 = 7
 *
 * NOTE: state is kept in plain global variables (not structs) on purpose --
 * Arduino's automatic function-prototype generator inserts prototypes at
 * the very top of the file, before any struct definitions exist yet, which
 * breaks compilation for functions that take a struct by reference. Plain
 * globals sidestep that entirely.
 */

// ---------------- Shared hardware config ----------------
const float V_REF = 5.0;
const float R_BITS = 10.0;
const float ADC_STEPS = (1 << int(R_BITS)) - 1;
const int potentiometerPin = A3;
const int NUM_LEVELS = 64;                 // 6-bit attenuator -> indices 0..63

const unsigned long SETTLE_MS = 5;         // settle time after switching attenuator, before reading ADC
const unsigned long CYCLE_DELAY_MS = 50;   // pacing between rounds -- tune for plotter readability

// How far the voltage has to drift from its converged value before an
// algorithm abandons its lock and searches again. Set this to whatever
// makes sense for your noise floor vs. real signal changes.
const float RECAL_DRIFT_VOLTS = 0.1;

// ---------------- Shared threshold & tolerance ----------------
// All four algorithms now aim for the same target. Linear only ever needed
// a threshold (its stop condition is a plain <= check, no tolerance band),
// so it uses THRESHOLD directly with no separate tolerance of its own.
const float THRESHOLD = 1.3;
const float TOLERANCE = 0.01;

// ---------------- Shared low-level hardware helpers ----------------
// (Same structure as the interpolation search file: toBinary / setVoltage /
// getVoltage / measureAt. This is the ONE place that touches shared
// hardware -- every algorithm's step funnels through here, one at a time.)

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

// ================= Linear search =================
int lin_i = 0;
bool lin_converged = false;
float lin_lastVoltage = 0;
int lin_convergedIndex = 0;
float lin_baselineVoltage = 0;

void resetLinear() {
  lin_i = 0;
  lin_converged = false;
  lin_lastVoltage = 0;
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
  lin_lastVoltage = v;
  if (v <= THRESHOLD || lin_i >= NUM_LEVELS - 1) {
    lin_converged = true;
    lin_convergedIndex = lin_i;
    lin_baselineVoltage = v;
    return THRESHOLD;
  } else {
    lin_i++;
  }
  return v;
}

// ================= Binary search =================
int bin_left = 0;
int bin_right = NUM_LEVELS - 1;
bool bin_converged = false;
float bin_lastVoltage = 0;
int bin_convergedIndex = 0;
float bin_baselineVoltage = 0;

void resetBinary() {
  bin_left = 0;
  bin_right = NUM_LEVELS - 1;
  bin_converged = false;
  bin_lastVoltage = 0;
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
    bin_convergedIndex = bin_left;
    bin_baselineVoltage = v;
    bin_converged = true;
    return THRESHOLD;
  }

  int mid = bin_left + (bin_right - bin_left) / 2;
  float v = measureAt(mid);
  bin_lastVoltage = v;
  if (abs(v - THRESHOLD) <= TOLERANCE) {
    bin_convergedIndex = mid;
    bin_baselineVoltage = v;
    bin_converged = true;
    return THRESHOLD;
  } else if (v < THRESHOLD) {
    bin_right = mid;
  } else {
    bin_left = mid + 1;
  }
  return v;
}

// ================= Interpolation search =================
// Matches the original file's math exactly: measureAt(left) and
// measureAt(right) are recomputed every iteration (no caching), same
// interpolation formula, same branch logic. Only addition is constrain()
// on pos as a safety net against out-of-range attenuator indices.
int interp_left = 0;
int interp_right = NUM_LEVELS - 1;
bool interp_converged = false;
float interp_lastVoltage = 0;
int interp_convergedIndex = 0;
float interp_baselineVoltage = 0;

void resetInterp() {
  interp_left = 0;
  interp_right = NUM_LEVELS - 1;
  interp_converged = false;
  interp_lastVoltage = 0;
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
    interp_convergedIndex = interp_left;
    interp_baselineVoltage = v;
    interp_converged = true;
    return THRESHOLD;
  }

  float voltLeft = measureAt(interp_left);
  float voltRight = measureAt(interp_right);

  if (voltRight == voltLeft) { // guard against divide-by-zero
    interp_convergedIndex = interp_left;
    interp_baselineVoltage = voltLeft;
    interp_converged = true;
    return THRESHOLD;
  }

  int pos = interp_left + (int)((THRESHOLD - voltLeft) * (interp_right - interp_left) /
                                 (voltRight - voltLeft));
  pos = constrain(pos, interp_left, interp_right);

  float v = measureAt(pos);
  interp_lastVoltage = v;

  if (abs(v - THRESHOLD) <= TOLERANCE) {
    interp_convergedIndex = pos;
    interp_baselineVoltage = v;
    interp_converged = true;
    return THRESHOLD;
  } else if (v < THRESHOLD) {
    // measured too low -> voltage decreases as index increases on this
    // hardware, so "too low" means we need a LOWER index -> shrink right
    interp_right = pos - 1;
  } else {
    // measured too high -> need a HIGHER index -> shrink left
    interp_left = pos + 1;
  }
  return v;
}

// ================= Fibonacci search =================
// f1/f2 are always kept as genuine consecutive Fibonacci numbers. The
// original file's update branches reused a variable right after
// overwriting it on the previous line, which broke that invariant (f2
// could collapse to 0 and end the search prematurely). Fixed here with
// temp variables -- same branch conditions and same offset/index logic
// as the original, just correct arithmetic.
int fib_fm, fib_f1, fib_f2, fib_offset;
bool fib_converged = false;
bool fib_finalCheckDone = false;
float fib_lastVoltage = 0;
int fib_convergedIndex = 0;
float fib_baselineVoltage = 0;

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
    fib_lastVoltage = v;
    if (abs(v - THRESHOLD) <= TOLERANCE) {
      fib_convergedIndex = index;
      fib_baselineVoltage = v;
      fib_converged = true;
      return THRESHOLD;
    } else if (v < THRESHOLD) {
      // measured too low -> need a LOWER index -> move left: shrink from
      // the top, keep the same offset, don't advance past this index
      int newF1 = fib_f1 - fib_f2;
      int newF2 = fib_f2 - newF1;
      fib_f1 = newF1;
      fib_f2 = newF2;
    } else {
      // measured too high -> need a HIGHER index -> move right: discard
      // everything up to and including this index, advance offset
      int newF1 = fib_f2;
      int newF2 = fib_f1 - fib_f2;
      fib_f1 = newF1;
      fib_f2 = newF2;
      fib_offset = index;
    }
  } else if (!fib_finalCheckDone) {
    fib_finalCheckDone = true;
    int lastIndex = fib_offset + 1;
    float v = fib_lastVoltage;
    if (lastIndex < NUM_LEVELS) {
      v = measureAt(lastIndex);
      fib_lastVoltage = v;
    }
    fib_convergedIndex = (lastIndex < NUM_LEVELS) ? lastIndex : fib_offset;
    fib_baselineVoltage = v;
    fib_converged = true;
    return THRESHOLD;
  }
  return fib_lastVoltage;
}

// ================= Setup =================
void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  Serial.begin(9600);
  Serial.println(ADC_STEPS);

  resetLinear();
  resetBinary();
  resetInterp();
  resetFib();
}

// ================= Main loop =================
// Each pass: every algorithm takes exactly one turn on the shared hardware,
// then we print all four current values (plus reference threshold lines)
// on a single line for the Serial Plotter.
void loop() {
  float vLinear = stepLinear();
  float vBinary = stepBinary();
  float vInterp = stepInterpolation();
  float vFib    = stepFibonacci();

  // Full-scale endpoint readings, same as writeVoltage() in the original
  // interpolation file (Max = attenuator index 0, Min = index 63). These
  // cost two extra hardware turns per pass, sampled once for everyone
  // rather than once per algorithm, since the physical extremes don't
  // depend on which algorithm's turn it is.
  float maxVoltage = measureAt(0);
  float minVoltage = measureAt(NUM_LEVELS - 1);

  Serial.print("Linear:");   Serial.print(vLinear, 3);
  Serial.print(", Binary:");  Serial.print(vBinary, 3);
  Serial.print(", Interp:");  Serial.print(vInterp, 3);
  Serial.print(", Fib:");     Serial.print(vFib, 3);
  Serial.print(", Max:");     Serial.print(maxVoltage, 3);
  Serial.print(", Min:");     Serial.print(minVoltage, 3);
  Serial.print(", Thresh:"); Serial.print(THRESHOLD, 3);   // reference line
  Serial.println();

  delay(CYCLE_DELAY_MS);
}
