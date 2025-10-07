#include <Wire.h>
#include <MPU6050_tockn.h>

MPU6050 mpu(Wire);

void setup() {
  Serial.begin(115200);   // Start serial communication at 115200 baud
  Wire.begin();           // Initialize I2C communication
  mpu.begin();            // Initialize MPU6050 sensor
  mpu.calcGyroOffsets();  // Calibrate gyro (keep MPU6050 still during this)
  
  Serial.println("MPU6050 is ready and calibrated!");
  delay(2000);
}

void loop() {
  mpu.update(); // Update sensor readings

  
  float roll = mpu.getAngleX();
  float pitch = mpu.getAngleY();
  float yaw = mpu.getAngleZ();

  // Print them to the serial monitor
  Serial.print("Roll: ");
  Serial.print(roll);
  Serial.print(" | Pitch: ");
  Serial.print(pitch);
  Serial.print(" | Yaw: ");
  Serial.println(yaw);

  delay(200); // Small delay to avoid flooding serial output
}
