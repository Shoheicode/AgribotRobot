import pygame
import serial
import time
import sys

# Setup serial to ESP32
ser = serial.Serial("COM3", 115200)  # Adjust COM port
time.sleep(2)

pygame.init()
pygame.joystick.init()

# Initialize the first connected joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected.")
    sys.exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")

screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("Joystick Motor Control")

print("Use left stick to control. ESC to quit.")

last_sent = ""
clock = pygame.time.Clock()

# Maximum motor power (scale to 0–100)
MAX_POWER = 64


def send_command(speed1, speed2):
    global last_sent
    # Round and format speeds
    s1 = int(speed1)
    s2 = int(speed2)
    command = f"{s1},{s2}\n"
    if command != last_sent:
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
        last_sent = command


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # Read joystick axes
    pygame.event.pump()
    axis_y = -joystick.get_axis(1)  # Forward/backward (invert so up = +)
    axis_y2 = joystick.get_axis(3)  # Right stick Y (optional, for additional control)
    # axis_x = joystick.get_axis(0)  # Left/right

    # Tank drive mixing
    left_power = (axis_y) * MAX_POWER
    right_power = (axis_y2) * MAX_POWER

    # Clamp values to range [-100, 100]
    left_power = max(-MAX_POWER, min(MAX_POWER, left_power))
    right_power = max(-MAX_POWER, min(MAX_POWER, right_power))

    send_command(left_power, right_power)
    print(f"Left: {left_power}, Right: {right_power}")

    clock.tick(30)

ser.close()
pygame.quit()
sys.exit()
