#include <Arduino.h>
#include <Servo.h>

// Ultrasonic Sensor Pins
const int trigPin = 9;
const int echoPin = 10;

// Servo Motor
Servo myServo;
const int servoPin = 11;
int defaultAngle = 0;
int activeAngle = 180;

// Detection Parameters
const int detectionThreshold = 10; // Distance in cm to trigger detection

// State tracking
bool objectDetected = false;
unsigned long lastDistanceCheck = 0;
unsigned long servoActivationTime = 0;
bool servoActive = false;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myServo.attach(servoPin);
  myServo.write(defaultAngle);
  
  // Wait for serial connection
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("RVMachine Initialized");
}

float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2; // Convert to cm
}

void loop() {
  unsigned long currentMillis = millis();

  // Check for commands from Python
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Move servo when AI detection is confirmed
    if (command == "ACTIVATE_SERVO") {
      myServo.write(activeAngle);
      servoActive = true;
      servoActivationTime = currentMillis;
      
      // Send confirmation
      Serial.println("SERVO_ACTIVATED");
    }
  }

  // Check if servo has been active for 5 seconds and needs to return
  if (servoActive && (currentMillis - servoActivationTime >= 5000)) {
    myServo.write(defaultAngle);
    servoActive = false;
  }

  // Check distance every 300ms
  if (currentMillis - lastDistanceCheck > 300) {
    float distance = getDistance();
    lastDistanceCheck = currentMillis;

    // Update object detection status
    bool previouslyDetected = objectDetected;
    objectDetected = (distance < detectionThreshold && distance > 0);

    // Only send status messages when the status changes
    if (objectDetected != previouslyDetected) {
      if (objectDetected) {
        Serial.println("OBJECT_DETECTED");
      } else {
        Serial.println("OBJECT_CLEAR");
      }
    }
  }

  delay(50); // Small delay to keep the loop responsive
}