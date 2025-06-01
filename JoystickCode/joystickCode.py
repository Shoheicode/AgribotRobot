import pygame
import serial
import time

# Init joystick
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Set up serial port (adjust COM port and baud)
ser = serial.Serial("COM4", 115200)  # Replace COM4 with your ESP32 port
time.sleep(2)

print("Sending joystick data to ESP32...")

while True:
    pygame.event.pump()

    # Axis 1 is usually vertical (Y axis)
    y_axis = -joystick.get_axis(1)  # Invert (up = positive)
    speed = int(y_axis * 127)  # Scale for RoboClaw
    direction = 1 if speed > 0 else (-1 if speed < 0 else 0)

    # Format: speed,direction\n
    data = f"{abs(speed)},{direction}\n"
    ser.write(data.encode("utf-8"))

    time.sleep(0.05)
