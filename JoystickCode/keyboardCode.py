import pygame
import serial
import time
import sys

# Configure serial port
ser = serial.Serial("COM3", 115200)  # Replace COM4 with your ESP32 port
time.sleep(2)

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("ESP32 Motor Control")

print("Keyboard control ready. Use W/S/X to send commands.")

# Motor control state
speed_value = 127
current_direction = 0


def send_command(speed, direction):
    command = f"{speed},{direction}\n"
    ser.write(command.encode())
    print(f"Sent: {command.strip()}")


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            key = event.key

            if key == pygame.K_w:
                current_direction = 1
                send_command(speed_value, current_direction)

            elif key == pygame.K_s:
                current_direction = -1
                send_command(speed_value, current_direction)

            elif key == pygame.K_x:
                current_direction = 0
                send_command(0, current_direction)

            elif key == pygame.K_ESCAPE:
                running = False

# Clean up
ser.close()
pygame.quit()
sys.exit()
